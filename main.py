from persica.context.application import ApplicationContext
from persica.applicationbuilder import ApplicationBuilder


def main():
    app = (
        ApplicationBuilder()
        .set_application_context_class(ApplicationContext)
        .set_scanner_packages(["src.core", "src.plugins", "src.route"])
        .build()
    )
    app.run()


if __name__ == "__main__":
    main()
