from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class GracefulPaginator(Paginator):
    def page(self, number):
        try:
            number = self.validate_number(number)
        except PageNotAnInteger:
            number = 1
        except EmptyPage:
            number = self.num_pages
        return super().page(number)
