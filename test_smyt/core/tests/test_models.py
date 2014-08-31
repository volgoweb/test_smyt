from django.test import TestCase
from test_smyt.core.models import *
from django.utils import timezone
from django.core.urlresolvers import reverse

class TaskTest(TestCase):
    def get_model(self):
        return factory.get_model_class('task')

    def create_task(self, title = 'only a test', priority = 1, due_date = timezone.now()):
        Task = self.get_model()
        return Task.objects.create(title = title, priority = priority, due_date = due_date)

    def test_task_creation(self):
        Task = self.get_model()
        m = self.create_task()
        self.assertTrue(isinstance(m, Task))
        self.assertEqual(m.title, 'only a test')

class ProjectTest(TestCase):
    def get_model(self):
        return factory.get_model_class('project')

    def create_project(self, name = 'only a test', tasks_count = 1):
        Project = self.get_model()
        return Project.objects.create(name = name, tasks_count = tasks_count)

    def test_project_creation(self):
        Project = self.get_model()
        m = self.create_project()
        self.assertTrue(isinstance(m, Project))
        self.assertEqual(m.name, 'only a test')
