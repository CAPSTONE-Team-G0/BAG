

Load `style.css` on every page from `base.html`.
Then load the page-specific stylesheet in that page template using `{% block extra_css %}`.

Example:

```html
{% block extra_css %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/profilestyle.css') }}">
{% endblock %}

{% block content %}

```



- `dashboard.html`, `dashboard_empty.html` → `dashboardstyle.css`
- `semesters.html`, `semester_new.html`, `semester_edit.html` → `semestersstyle.css`
- `aid_new.html`, `aid_edit.html` → `fundsstyle.css`
- `transaction_new.html`, `transaction_edit.html` → `expensestyle.css`
- `categories.html` → `categoriesstyle.css`
- `profile.html` → `profilestyle.css`
- `parent_access.html`, `parent_dashboard.html` → `parentstyle.css`
- `faqs.html` and `faq_sections/*` → `faqsstyle.css`
- `login.html`, `register.html`, `forgot_password.html`, `reset_password.html` → `miscstyle.css`
-  intro pages → `introstyle.css`
