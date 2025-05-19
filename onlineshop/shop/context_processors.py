from common.models import Categories


def categories_processor(request):
    categories = Categories.objects.filter(is_visible=True)
    context = {'categories': categories}
    return context
