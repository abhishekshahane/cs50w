# Various imports from django
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from markdown2 import Markdown
from django import forms

# Imports for util functions, and random.choice

from . import util
from random import choice

# Creating a new class for the user to create a form
class CreateForm(forms.Form):
    title = forms.CharField(label='', widget=forms.TextInput(attrs={'id': 'title'}))
    textarea = forms.CharField(widget=forms.Textarea(attrs={'cols': '10'}),  label='')

# A new class for the user to edit forms 

class EditForms(forms.Form):
    textarea = forms.CharField(widget=forms.Textarea(attrs={'cols': '10'}),  label='')

# Index Page 

def index(request):
    """
    Displays a list of all the entries. 
    """
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

# Content Page(s)

def content(request, title):
    """
    Displays the content of a particular entry(page).
    """
    # If we don't find the entry, then we display the 404 page
    if util.get_entry(title) == None:
        return render(request, "encyclopedia/404.html", {
            "name": title,
             "word": "find"
        })

    # If we find the entry, then we convert the markdown to HTML, and display it.
    a = util.get_entry(title)
    converter = Markdown()
    html = converter.convert(a)
    #print(html)
    return render(request, "encyclopedia/page.html",{
        "title": title,
        "content": html
    })

def random(request):
    """
    Redirects to a random page. 
    """
    li = util.list_entries()
    f = choice(li)
    #print(f)
    return HttpResponseRedirect(f'/wiki/{f}')

def search(request):
    """
    Searches for an entry in the wiki. 
    """
    # GETting the request
    q = request.GET.get('q').strip()
    li = util.list_entries()
    f = []

    # We redirect user to the page immediately, if the entry matches a page 
    if q in li:
        return HttpResponseRedirect(reverse('encyclopedia:page', args=[q]))
    # It might be a substring - Even if it isn't, {% empty %} handles that

    for each in li:
        if q.lower() in each.lower():
            f+=[each]

    if len(f)==1:
        result = "result"

    else:
        result="results"

    # We render the HTML page, having access to the following variables

    return render(request, "encyclopedia/search.html",{
        "f": f,
        "number": len(f),
        "result": result
    })

def create(request):
    """
    Helps the user to create a new entry. 
    """
    
    # Checking if it is a POST request, if it is, then we get the cleaned data
    if request.method == "POST":
        form = CreateForm(request.POST)

        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["textarea"]

            # Saving the entry 
        
            if title.lower() not in [each.lower() for each in util.list_entries()]:
                util.save_entry(title, content)
                return HttpResponseRedirect(reverse("encyclopedia:page", args=[title]))

            else:
                return render(request, "encyclopedia/create.html",
                {
                "form": form,
                "title_exists": True
            })
        else:
            return render(request, "encyclopedia/create.html",
            {
                "form": form
            })
    else:
        return render(request, "encyclopedia/create.html",
        {
            "form": CreateForm()
        })

def edit(request, title):
    """
    Helps the user to edit an existing entry. 
    """
    if util.get_entry(title) == None:
        return render(request, "encyclopedia/404.html", 
        {
            "name" : title,
            "word" : "edit"
        })
    else:
        if request.method == "POST":
            form = EditForms(request.POST)
            if form.is_valid():
                # If the form is valid, then we will get the cleaned_data and update the entry
                content = form.cleaned_data["textarea"]
                util.save_entry(title, content)
                return HttpResponseRedirect(reverse("encyclopedia:page", args=[title]))
        content = util.get_entry(title)
        # Simulating a POST request to fill in, the best alternative is a hashmap
        data = {
            'title': title, 
            'textarea': content
        }
        # Render the page with the data pre-populated in the textarea(and title)
        return render(request, "encyclopedia/edit.html", {
            "form": EditForms(data),
            "title": title
        })