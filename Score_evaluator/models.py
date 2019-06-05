# -*- coding: utf-8 -*
from django.db import models

from allauth.socialaccount.models import SocialAccount


class Category(models.Model):
    id = models.CharField(max_length=40, primary_key=True)
    name = models.CharField(max_length=100)
    likes = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = "Category"
        verbose_name_plural = "categories"


class CategoryScore(models.Model):
    user = models.ForeignKey(SocialAccount, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    score = models.FloatField()

    def __str__(self):
        return str(self.user.user) + "'s score for " + str(self.category.name)

    def get_category_id(self):
        return self.category.id

    class Meta:
        managed = True
        models.UniqueConstraint(fields=['user', 'category'], name="userCategory")
        db_table = "CategoryScore"


