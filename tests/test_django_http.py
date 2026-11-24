from django.urls import reverse


def test_list_uses_template_and_two_queries(web_client, django_repair, django_assert_num_queries):
    with django_assert_num_queries(2):
        response = web_client.get("/")
    assert response.status_code == 200
    assert response.templates[0].name == "repairdesk/list.html"
    assert b"REP-031" in response.content
    assert b"Brake cleaning" in response.content


def test_detail_found(web_client, django_repair):
    response = web_client.get(reverse("repair-detail", args=[django_repair.pk]))
    assert response.status_code == 200
    assert response.templates[0].name == "repairdesk/detail.html"
    assert b"Brake noise" in response.content


def test_unknown_repair_is_404(web_client, db):
    assert web_client.get("/repairs/65431/").status_code == 404


def test_workbench_redirects_guest(web_client):
    response = web_client.get("/workbench/")
    assert response.status_code == 302
    assert response["Location"] == "/accounts/login/?next=/workbench/"


def test_workbench_works_for_signed_in_user(web_client, rider_account, django_repair):
    web_client.force_login(rider_account)
    response = web_client.get("/workbench/")
    assert response.status_code == 200
    assert b"REP-031" in response.content


def test_search_trims_input_and_filters(web_client, django_repair):
    matches = web_client.get("/", {"q": "  BRAKE "})
    assert list(matches.context["repairs"]) == [django_repair]
    misses = web_client.get("/", {"q": "%"})
    assert list(misses.context["repairs"]) == []
