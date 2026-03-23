import strawberry

@strawberry.input
class PaginationInput:
    page: int = 1
    page_size: int = 20
