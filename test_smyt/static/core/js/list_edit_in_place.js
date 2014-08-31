// Базовый объект фронтенда
var app = {
  models: {},
  collections: {},
  views: {},
  routers: {},
  models_structures: {},
  // css-идентификатор списка моделей
  models_list: '.models-list',
  // css-идентификатор описания структуры выбранной модели
  model_structure: '.model-info-structure__list',
  // css-идентификатор названий полей модели списка объектов
  model_list_headers: '.model-info-objects__list thead',
  // css-идентификатор списка объектов
  model_list_objects: '.model-info-objects__list tbody',
  // название выбранной модели
  chosen_model_name: '',
};

$(document).ready(function () {
    // получаем структуру всех моделей
    get_models_structures();
});

/**
 * Метод, формирующий страницу при выборе модели в списке.
 */
app.activate_model = function() {
    app.models.Model = Backbone.Model.extend({
      defaults: {
        id: '',
      },

      validate: function(attrs, options) {
        var errors = [];
        _.each(app.models_structures[app.chosen_model_name], function(ftype, fname) {
            if (ftype == 'integer') {
                if (!$.isNumeric(attrs[fname])) {
                    errors.push(fname + ': должно быть числом.');
                }
            }
            
            if (ftype == 'date') {
                var pattern = /(\d{2})\.(\d{2})\.(\d{4})/;
                var dt = Date.parse(attrs[fname].replace(pattern,'$3-$2-$1'));
                if (isNaN(dt)) {
                    errors.push(fname + ': некорректная дата.');
                }
            }
        });
        if (errors.length > 0) {
            alert(errors.join("\r\n"));
            return true;
        }
        return false;
      },
    });

    /**
     * коллекция объектов
     */
    app.collections.Collection = Backbone.Collection.extend({
      model: app.models.Model,
      url: '/core/json/' + app.chosen_model_name + '/',
    });

    app.collections.collection = new app.collections.Collection();

    /**
     * Представление модели
     */
    app.views.ModelView = Backbone.View.extend({
      tagName: 'tr',

      template: _.template($('#object-edit-item-template').html()),

      events: {
        'click .edit-btn': 'edit',
        'click .save-btn': 'save',
      },

      initialize: function() {
        this.listenTo(this.model, 'change', this.render);
        this.listenTo(this.model, 'destroy', this.remove);
      },

      render: function() {
        var tpl_vars = {fields: [],};
        model_json = this.model.toJSON();
        _.each(app.models_structures[app.chosen_model_name], function(val, key) {
          tpl_vars.fields.push({
            type: val,
            name: key,
            value: model_json[key],
          })
        });
        var html = this.template(tpl_vars);

        $('.date-form-field').not('.processed').datepicker({format: 'dd.mm.yyyy'});
        $('.date-form-field').addClass('processed');

        this.$el.html(html);

        var that = this
        _.each(app.models_structures[app.chosen_model_name], function(ftype, fname) {
            if (ftype != 'id') {
                that[fname + '_input'] = that.$('.edit-' + fname);
            }
        });
        return this;
      },

      edit: function() {
        this.$el.addClass('editing');
      },

      save: function() {
          this.model.save(get_values_from_inputs(this), { validate: true });
          this.$el.removeClass('editing');
      },
    });

    /**
     * Представление коллекции
     */
    app.views.CollectionView = Backbone.View.extend({
      el: $(app.model_list_objects),
      
      events: {
        'click #add-btn': 'createNewModel',
      },

      initialize: function() {
        var that = this
        _.each(app.models_structures[app.chosen_model_name], function(ftype, fname) {
            if (ftype != 'id') {
                that[fname + '_input'] = $('.add-' + fname);
            }
        });

        this.list = $(this.el);

        this.listenTo(app.collections.collection, 'add', this.addOne);
        this.listenTo(app.collections.collection, 'reset', this.addAll);
        this.listenTo(app.collections.collection, 'all', this.render);

        app.collections.collection.fetch();
      },

      addOne: function(model) {
        var model_view = new app.views.ModelView({model: model});
        this.list.append(model_view.render().el)
      },

      addAll: function() {
        app.collections.collection.each(this.addOne, this);
      },

      createNewModel: function() {
        var values = {};
        var that = this;
        var count_not_empty_fields = 0;
        _.each(app.models_structures[app.chosen_model_name], function(ftype, fname) {
            if (that[fname + '_input'] !== undefined) {
                values[fname] = that[fname + '_input'].val();
                if (values[fname]) {
                    count_not_empty_fields++;
                }
            }
        });
        if (count_not_empty_fields > 0) {
            save_result = app.collections.collection.create(values, {wait: true, validate: true,});
            if (save_result) {
                this.clearInputs();
            }
        }
      },

      clearInputs: function() {
          var that = this;
          _.each(app.models_structures[app.chosen_model_name], function(ftype, fname) {
              if (fname + '_input' in that) {
                that[fname + '_input'].val('');
              }
          });
      },
    }); // app.views.CollectionView

    app.views.collectionView = new app.views.CollectionView();
}; // app.activate_model

/**
 * Получение структуры всех имеющихся моделей.
 */
function get_models_structures() {
  $.ajax({
    url: '/core/json/models-structure/',
    type: 'GET',
    success: function(data) {
      app.models_structures = data;
      render_models_names();
    },
  })
}

/**
 * Вывод на страницу списка моделей.
 */
function render_models_names() {
  if ($(app.models_list).hasClass('rendered')) {
    return;
  }

  for (var m in app.models_structures) {
    var li = $('<li>').text(m);
    $(app.models_list).append(li);
    li.bind('click', function() {
      app.chosen_model_name = $(this).text();
      render_model_structure();
      render_objects_list();
      $(app.models_list).find('li').removeClass('active');
      $(this).addClass('active');
    });
  }

  $(app.models_list).find('li').eq(0).click();
}

/**
 * Вывод на страницу структуру выбранной модели.
 */
function render_model_structure() {
  var model_structure = app.models_structures[app.chosen_model_name];
  $(app.model_structure).html(JSON.stringify(model_structure));
}

/**
 * Вывод на страницу списка объектов выбранной модели.
 */
function render_objects_list() {
  var tpl = _.template($('#objects-list-headers-template').html());
  $(app.model_list_headers).html(tpl({
    model_structure: app.models_structures[app.chosen_model_name],
  }));

  tpl = _.template($('#object-add-item-template').html());
  tpl_vars = {fields: [],};
  _.each(app.models_structures[app.chosen_model_name], function(val, key) {
    tpl_vars.fields.push({
      type: val,
      name: key,
      value: '',
    })
  });
  $(app.model_list_objects).html('<tr>' + tpl(tpl_vars) + '</tr>');

  app.activate_model();
}

/**
 * Получение значений из полей редактирования/добавления объекта
 */
function get_values_from_inputs(obj) {
    var values = {};
    _.each(app.models_structures[app.chosen_model_name], function(ftype, fname) {
        if (ftype != 'id') {
            values[fname] = obj[fname + '_input'].val();
        }
    });
    return values;
}
