
    if not msg:
        msg = request.GET.get("msg", "")
    if msg:
        msg += '<br/><br/>'
    user = request.GET.get("user", "") or request.user
    if user and user.is_authenticated:
        msg += f'U bent ingelogd als <i>{user.username}</i>.'
        msg += ' Klik <a href="/logout/?next=/">hier</a> om uit te loggen'
    else:
        msg += ('U bent niet ingelogd.'
                ' Klik <a href="accounts/login/?next=/">hier</a> om in te loggen,'
                ' <a href="/">hier</a> om terug te gaan naar het begin.')
