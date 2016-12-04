class WordPressRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'wordpress':
            return 'wordpress'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'wordpress':
            return 'wordpress'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'wordpress' or obj2._meta.app_label == 'wordpress':
            return True
        return None

    def allow_syncdb(self, db, model):
        return model._meta.app_label != 'wordpress'


