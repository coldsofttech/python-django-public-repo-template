"""Pagination with bounds, so absurd values cannot overflow the database."""

from rest_framework.pagination import LimitOffsetPagination
from rest_framework.request import Request


class BoundedLimitOffsetPagination(LimitOffsetPagination):
    """``limit`` and ``offset`` pagination with an upper bound on both."""

    default_limit = 50
    max_limit = 100
    max_offset = 2**31 - 1  # fits every database integer type

    def get_offset(self, request: Request) -> int:
        return min(super().get_offset(request), self.max_offset)
