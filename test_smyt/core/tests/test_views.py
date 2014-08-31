from django.test import TestCase
from django.core.urlresolvers import reverse
from test_smyt.core.tests.test_models import *
from test_smyt.core.views import BackboneView
from test_smyt.core.models import *
from django.test import RequestFactory
from django.utils import timezone
import json

class ModelsStructureTest(TestCase):
    def test_get_model_structure(self):
        url = reverse('test_smyt.core.views.get_models_structures')
        kwargs = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        resp = self.client.get(url, **kwargs)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('task', resp.content)
        self.assertIn('title', resp.content)
        self.assertIn('priority', resp.content)
        self.assertIn('due_date', resp.content)
        self.assertIn('project', resp.content)
        self.assertIn('name', resp.content)
        self.assertIn('tasks_count', resp.content)

    def test_get_task_object(self):
        request_factory = RequestFactory()
        request = request_factory.get('/core/json/task/1')
        view = BackboneView.as_view()
        resp = view(request, model = 'task', id = 1)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('only a test', resp.content)

    def test_add_project_object(self):
        request_factory = RequestFactory()
        request = request_factory.put('/core/json/project', json.dumps({
            'name': 'only a test 2',
            'tasks_count': 3,
        }), content_type='application/json')
        view = BackboneView.as_view()
        resp = view(request, model = 'project', id = '')

        self.assertEqual(resp.status_code, 200)
        self.assertIn('only a test 2', resp.content)

