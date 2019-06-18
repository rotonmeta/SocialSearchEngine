# -*- coding: utf-8 -*
from django.db import models
from django.db.models import Sum

from allauth.socialaccount.models import SocialAccount


class Category(models.Model):
    id = models.CharField(max_length=40, primary_key=True)
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', null=True, on_delete=models.CASCADE)
    depth = models.IntegerField()

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = "Category"
        verbose_name_plural = "Categories"


class CategoryScore(models.Model):
    user = models.ForeignKey(SocialAccount, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    likes = models.IntegerField(default=0)
    real_value = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user.user) + "'s score for " + str(self.category.name)

    class Meta:
        managed = True
        models.UniqueConstraint(fields=['user', 'category'], name="userCategory")
        db_table = "CategoryScore"



