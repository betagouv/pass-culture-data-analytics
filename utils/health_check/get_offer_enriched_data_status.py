from read.postgresql_database.health_check_queries import HealthCheckSession


def get_offer_enriched_data_status(
        is_enriched_offer_present,
        is_enriched_offers_contains_data) -> dict:
    enriched_status = dict()
    enriched_status.update({
        'is_enriched_offer_datasource_exists': is_enriched_offer_present(HealthCheckSession),
        'is_offer_ok': is_enriched_offer_present(HealthCheckSession) and is_enriched_offers_contains_data(),
    })

    return enriched_status