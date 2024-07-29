"""__init__.py"""


def init_routes(app):
    from routes import arena_routes, crawl_routes, solr_routes

    app.include_router(solr_routes.router)
    app.include_router(arena_routes.router)
    app.include_router(crawl_routes.router)

    return app
