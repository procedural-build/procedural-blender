from .exceptions import MultipleObjectsReturned, DoesNotExist
from .auth import USER


class GenericViewSet():

    def __init__(self, base_path):
        self.base_path = base_path

    def object_path(self, object_id: str):
        return f'{self.base_path}{"" if self.base_path.endswith("/") else "/"}{f"{object_id}/" if object_id is not None else ""}'

    def get_or_create(
        self,
        query_params,
        create_params = None,
        create = False
    ):
        try:
            return self.get_by_query_params(query_params)
        except (DoesNotExist):
            if create:
                query_params.update(create_params or {})
                return self.create(query_params)
        return None

    def get_by_query_params(self, query_params):
        items = self.list(query_params)
        if (len(items) > 1):
            raise MultipleObjectsReturned("Found more than one object that matches those query params")
        elif len(items) == 0:
            raise DoesNotExist("No object found")
        return items[0]

    def list(self, query_params: dict=None):
        return USER[0].request(
            'GET',
            self.base_path,
            query_params=query_params
        )

    def retrieve(self, object_id, query_params: dict=None):
        return USER[0].request(
            'GET',
            self.object_path(objectId),
            query_params=query_params
        )

    def create(self, data, raw=False):
        return USER[0].request(
            'POST',
            self.base_path,
            data = data,
            raw = raw
        )

    def update(self, object_id, data, query_params=None, raw=False):
        return USER[0].request(
            'PUT',
            self.object_path(object_id),
            data = data,
            query_params = query_params,
            raw = raw
        )

    def partial_update(self, object_id, data, query_params=None, raw=False):
        return USER[0].request(
            'PATCH',
            self.object_path(object_id),
            data = data,
            query_params = query_params,
            raw = raw
        )

    def delete(self, object_id, query_params=None):
        return USER[0].request(
            'DELETE',
            self.object_path(object_id),
            query_params = query_params
        )
