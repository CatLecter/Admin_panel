from django.contrib.postgres.aggregates import ArrayAgg
from django.core import paginator
from django.core.paginator import PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView
from movies.models import FilmWork


class MoviesApiMixin:
    model = FilmWork
    http_method_names = ["get"]

    def get_queryset(self):
        """Метод возвращающий подготовленный QuerySet."""

        fields = [
            "id",
            "title",
            "description",
            "creation_date",
            "rating",
            "type",
        ]

        return (
            FilmWork.objects.order_by("title")
            .values(*fields)
            .annotate(
                genres=ArrayAgg(
                    "genres__name",
                    distinct=True,
                ),
                actors=ArrayAgg(
                    "persons__full_name",
                    filter=Q(personfilmwork__role="actor"),
                    distinct=True,
                ),
                directors=ArrayAgg(
                    "persons__full_name",
                    filter=Q(personfilmwork__role="writer"),
                    distinct=True,
                ),
                writers=ArrayAgg(
                    "persons__full_name",
                    filter=Q(personfilmwork__role="director"),
                    distinct=True,
                ),
            )
        )

    def render_to_response(self, context, **response_kwargs):
        """Метод, отвечающий за форматирование данных,
        которые вернутся при GET-запросе.
        """

        return JsonResponse(context)


class Movies(MoviesApiMixin, BaseListView):
    paginate_by = 50

    def get_context_data(self, *, object_list=None, **kwargs):
        """Метод, возвращающий словарь с данными для формирования страницы."""

        paginator, page, queryset, is_paginated = self.paginate_queryset(
            self.get_queryset(),
            self.paginate_by,
        )
        previous_page = page.previous_page_number() if page.has_previous() else None
        next_page = page.next_page_number() if page.has_next() else None

        return {
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "prev": previous_page,
            "next": next_page,
            "results": list(queryset),
        }


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):
    def get_context_data(self, *, object_list=None, **kwargs):
        """Метод, возвращающий словарь с данными для формирования страницы."""

        context_data = super().get_context_data(kwargs={"pk": self.get_object()["id"]})
        return context_data["object"]
