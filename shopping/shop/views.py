from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse_lazy
from django.forms.utils import ErrorList
from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from django.views.generic.edit import CreateView
from shop.models import ShoppingList, ShoppingListItem


def get_shoplist(id, owner):
    return get_object_or_404(ShoppingList, id=id,
                             owner=owner)


class ShopListView(LoginRequiredMixin, ListView):
    template_name = 'shop/shop_list.html'
    context_object_name = 'shoplists'

    def get_queryset(self):
        return ShoppingList.objects.filter(
            owner=self.request.user)


class ShopListCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    template_name = 'shop/shop_create.html'
    model = ShoppingList
    fields = ['name', 'budget']
    success_url = reverse_lazy('shop_list')
    success_message = 'Shoplist created successfully'

    def form_valid(self, form):
        name = form.cleaned_data['name']
        if ShoppingList.objects.filter(name=name, owner=self.request.user):
            form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList([
                u'Shopping list already exist'])
            return self.form_invalid(form)
        form.instance.owner = self.request.user
        return super(ShopListCreateView, self).form_valid(form)


class ShopListItemCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    template_name = 'shop/shop_list_item_create.html'
    model = ShoppingListItem
    fields = ['name']
    success_message = 'Item added to shopping list'

    def get_context_data(self, **kwargs):
        context = super(ShopListItemCreateView,
                        self).get_context_data(**kwargs)
        context['shoplist'] = get_shoplist(id=self.kwargs.get('shop_list_id', 0),
                                           owner=self.request.user)
        return context

    def form_valid(self, form):
        if form.is_valid():
            name = form.cleaned_data.get('name')
            shoplist = get_shoplist(id=self.kwargs.get('shop_list_id', 0),
                                    owner=self.request.user)
            if ShoppingListItem.objects.filter(name=name, shoplist=shoplist):
                form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                    [u'Item is already in shoplist'])
                return self.form_invalid(form)
            form.instance.shoplist = shoplist
            return super(ShopListItemCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('shop_list_items',
                            kwargs={'shop_list_id': self.kwargs.get('shop_list_id')})


class ShopListItemView(LoginRequiredMixin, ListView):
    template_name = 'shop/shop_list_item_list.html'
    context_object_name = 'shoplistitems'

    def get_queryset(self):
        shoplist = get_shoplist(id=self.kwargs.get('shop_list_id', 0),
                                owner=self.request.user)
        return ShoppingListItem.objects.filter(shoplist=shoplist)

    def get_context_data(self, **kwargs):
        shoplist = get_shoplist(id=self.kwargs.get('shop_list_id', 0),
                                owner=self.request.user)
        context = super(ShopListItemView, self).get_context_data(**kwargs)
        context['shoplist'] = shoplist
        return context
