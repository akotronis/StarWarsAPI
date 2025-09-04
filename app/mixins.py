class CommonFunctionalityViewsetMixin:
    """
    Mixin with common viewset functionality:
    - Filtering based on model field (`filter_field`).
      `Film` doesn't have a 'name' field, it has a 'title',
      so `filter_field` is overridden in the view.
    - Allowed http methods
    Inherit from this class to avoid code repetition.
    """
    http_method_names = ['get']
    filter_field = 'name'

    def get_queryset(self):
        queryset = super().get_queryset()
        if (filter_field_value := self.request.query_params.get('contains')):
            return queryset.filter(**{f'{self.filter_field}__contains': filter_field_value})
        return queryset