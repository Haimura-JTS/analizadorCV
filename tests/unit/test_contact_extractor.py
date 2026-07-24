from cv_analyzer.contact_extractor import extract_contact_info


def test_extract_contact_info_detects_email_phone_and_links() -> None:
    text = (
        "ana@example.com\n"
        "+34 600 123 456\n"
        "linkedin.com/in/ana\n"
        "github.com/ana\n"
        "ana.dev"
    )

    contact = extract_contact_info(text)

    assert contact.email == "ana@example.com"
    assert contact.phone == "+34 600 123 456"
    assert contact.linkedin == "https://linkedin.com/in/ana"
    assert contact.github == "https://github.com/ana"
    assert contact.portfolio == "https://ana.dev"


def test_extract_contact_info_returns_none_for_missing_values() -> None:
    contact = extract_contact_info("Sin datos de contacto")

    assert contact.email is None
    assert contact.phone is None
    assert contact.linkedin is None
    assert contact.github is None
    assert contact.portfolio is None


def test_extract_contact_info_does_not_treat_email_fragments_as_urls() -> None:
    contact = extract_contact_info(
        "alex.rivera@example.test\n"
        "linkedin.com/in/alex-rivera\n"
        "github.com/alex-rivera\n"
        "alexrivera.dev"
    )

    assert contact.linkedin == "https://linkedin.com/in/alex-rivera"
    assert contact.github == "https://github.com/alex-rivera"
    assert contact.portfolio == "https://alexrivera.dev"
