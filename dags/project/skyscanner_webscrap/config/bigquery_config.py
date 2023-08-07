from google.cloud import bigquery
schema_setting = {
    "flight_price" : {
        'source_format' : 'bigquery.SourceFormat.CSV',
        'field_delimiter' : '|',
        'skip_leading_rows' : 1,
        'schema' : [
            bigquery.SchemaField('flight_uuid', 'STRING'),
            bigquery.SchemaField('price', 'INTEGER'),
            bigquery.SchemaField('check_date', 'DATE')
        ]
    },
    "memo" : {
        'source_format' : 'bigquery.SourceFormat.CSV',
        'field_delimiter' : '|',
        'skip_leading_rows' : 1,
        'schema' : [
            bigquery.SchemaField('flight_uuid', 'STRING'),
            bigquery.SchemaField('memo', 'STRING'),
            bigquery.SchemaField('check_date', 'DATE')
        ]
    },
    "flight_go_plan" : {
        'source_format' : 'bigquery.SourceFormat.CSV',
        'field_delimiter' : '|',
        'skip_leading_rows' : 1,
        'schema' : [
                bigquery.SchemaField('flight_uuid', 'STRING'),
                bigquery.SchemaField('company', 'STRING'),
                bigquery.SchemaField('trans_paln', 'STRING'),
                bigquery.SchemaField('trans_cnt', 'INTEGER'),
                bigquery.SchemaField('takeoff_time', 'DATETIME'),
                bigquery.SchemaField('land_time', 'DATETIME'),
                bigquery.SchemaField('takeoff_location', 'STRING'),
                bigquery.SchemaField('land_location', 'STRING'),
                bigquery.SchemaField('spend_time', 'STRING'),
                bigquery.SchemaField('spend_hr', 'INTEGER'),
                bigquery.SchemaField('spend_min', 'INTEGER'),
                bigquery.SchemaField('check_date', 'DATE')
        ]
    }
}