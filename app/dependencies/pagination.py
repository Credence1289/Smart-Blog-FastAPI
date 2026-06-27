from fastapi import Query

#start from 1 and value should not be negative or greater than(ge) 1
#deafult value is 10 and greater than 1 anf less than (le)20
'''
ge >=
gt >
le <=
lt <
'''
def pagination_param(
        page:int = Query(
            default=1,
            ge=1,
            description="Page number"
        ),
        size:int = Query(
            default=1,
            ge=1,le=20,
            descriptiom="items per page"
        )
):
    return {
        "page": page,
        "size": size,
    }