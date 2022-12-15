from django.core.paginator import Paginator


POSTS_AMOUNT = 10


def pagntr(list, page_number):
    paginator = Paginator(list, POSTS_AMOUNT)
    return paginator.get_page(page_number)
