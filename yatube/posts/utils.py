from django.core.paginator import Paginator


POSTS_AMOUNT = 10


def pagntr(request, list):
    """Вывод на странице по 10 постов"""
    page_number = request.GET.get('page')
    paginator = Paginator(list, POSTS_AMOUNT)
    return paginator.get_page(page_number)
