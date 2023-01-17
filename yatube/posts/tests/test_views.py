from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Post, Group

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Текст',
            author=cls.user,
            group=Group.objects.create(
                title='Заголовок',
                slug='test_slug')
        )
        cls.templates_pages_names = {
            reverse("posts:index"): "posts/index.html",
            reverse(
                "posts:group_list", kwargs={"slug": cls.group.slug}
            ): "posts/group_list.html",
            reverse(
                "posts:profile", kwargs={"username": cls.post.author}
            ): "posts/profile.html",
            reverse(
                "posts:post_detail", kwargs={"post_id": cls.post.pk}
            ): "posts/post_detail.html",
            reverse(
                "posts:post_edit", kwargs={"post_id": cls.post.pk}
            ): "posts/create_post.html",
            reverse("posts:post_create"): "posts/create_post.html",
        }

    def setUp(self):
        # Создаем авторизованный клиент
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Проверяем, что при обращении к name вызывается соответствующий HTML-шаблон
        for name, template in self.templates_pages_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text = first_object.text
        post_author = first_object.author
        post_group = first_object.group.slug
        self.assertEqual(post_text,
                         self.post.text)
        self.assertEqual(post_author, self.post.author)
        self.assertEqual(post_group, self.post.group.slug)
        first_ten = list(Post.objects.all()[:10])
        self.assertEqual(list(response.context['page_obj']), first_ten)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse("posts:group_list", kwargs={"slug": self.group.slug})
        )
        first_ten = list(Post.objects.filter(group_id=self.group.id)[:10])
        self.assertEqual(list(response.context["page_obj"]), first_ten)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse("posts:profile", kwargs={'username': 'auth'})
        )
        first_ten = list(Post.objects.filter(author_id=self.user.id)[:10])
        self.assertEqual(list(response.context['page_obj']), first_ten)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        self.assertEqual(response.context.get('post').text, self.post.text)
        self.assertEqual(response.context.get('post').author, self.post.author)
        self.assertEqual(response.context.get('post').group, self.post.group)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, field in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, field)

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, field in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, field)

    def test_post_in_pages(self):
        """После создания поста, он появился на соответсвующих страницах."""
        form_fields = {
            reverse('posts:index'): Post.objects.get(group=self.post.group),
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ): Post.objects.get(group=self.post.group),
            reverse(
                'posts:profile', kwargs={'username': self.post.author}
            ): Post.objects.get(group=self.post.group),
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                form_field = response.context.get('page_obj')
                self.assertIn(expected, form_field)

    def test_group_of_post(self):
        """Пост не попал в группу, для которой не был предназначен."""
        form_fields = {
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ): Post.objects.exclude(group=self.post.group),
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                form_field = response.context['page_obj']
                self.assertNotIn(expected, form_field)
