  var app = {
    models: {},
    collections: {},
    views: {},
    routers: {},
  };
  $(document).ready(function () {

  // app.init = function() {
    // var now = new Date();
    // var now_str = ('0' + date.getDate()).slice(-2) + '-' + ('0' + (date.getMonth() + 1)).slice(-2) + '-' +  date.getFullYear()

    // модель задачи
    app.models.Task = Backbone.Model.extend({
      defaults: {
        id: '',
        title: '',
        priority: '',
        due_date: '',
      }
    });

    // коллекция задач
    app.collections.TaskCollection = Backbone.Collection.extend({
      model: app.models.Task,
      url: '/tasks/json/'
    });

    app.collections.tasks = new app.collections.TaskCollection();

    app.views.TaskView = Backbone.View.extend({
      tagName: 'tr',

      template: _.template($('#task-item-template').html()),

      events: {
        'click .edit-btn': 'edit',
        'click .save-btn': 'save',
      },

      initialize: function() {
        this.listenTo(this.model, 'change', this.render);
        this.listenTo(this.model, 'destroy', this.remove);
      },

      render: function() {
        this.$el.html(this.template(this.model.toJSON()));
        this.title_edit = this.$('.edit-title');
        this.priority_edit = this.$('.edit-priority');
        this.due_edit = this.$('.edit-due_date');
        return this;
      },

      edit: function() {
        this.$el.addClass('editing');
      },

      save: function() {
        var title = this.title_edit.val();
        if (!title) {
          this.model.destroy();
        }
        else {
          this.model.save({
            title: title,
            priority: this.priority_edit.val(),
            due_date: this.due_edit.val(),
          });
          this.$el.removeClass('editing');
        }
      },
     
    });

    app.views.TasksView = Backbone.View.extend({
      el: $('#tasks-list'),
      
      events: {
        'click #add-btn': 'createNewTask',
      },

      initialize: function() {
        // this.id = this.$('.add-id');
        this.title = this.$('.add-title');
        this.priority = this.$('.add-priority');
        this.due_date = this.$('.add-due_date');
        this.list = $('#tasks-list');

        this.listenTo(app.collections.tasks, 'add', this.addOne);
        this.listenTo(app.collections.tasks, 'reset', this.addAll);
        this.listenTo(app.collections.tasks, 'all', this.render);

        app.collections.tasks.fetch();
      },

      addOne: function(model) {
        var model_view = new app.views.TaskView({model: model});
        this.list.append(model_view.render().el)
      },

      addAll: function() {
        app.collections.tasks.each(this.addOne, this);
      },

      createNewTask: function() {
        console.log('add');
        app.collections.tasks.create({
          // id: this.id,
          title: this.title.val(),
          priority: this.priority.val(),
          due_date: this.due_date.val(),
        });
        this.title.val('');
        this.priority.val('');
        this.due_date.val('');
      },
    })
  // };

  // app.run = function() {
  // };

    // app.init();
    // app.run();
    app.views.tasksView = new app.views.TasksView();
  });

