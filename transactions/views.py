from datetime import datetime
from django.db.models import Count
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from .models import SanctionRecord, NameVariation
from .name_variations import generate_name_variations  # Import your name variation generator

#------------------------------------------------------------------CRUD VARIATIONS OPERATIONs------------------------


def delete_variation(request, variation_id):
    variation = get_object_or_404(NameVariation, variation_id=variation_id)
    variation.delete()
    return redirect("transactions:view_record", record_id=variation.sanction_record.id)  # Adjusted to pass record_id

def update_variation(request, variation_id):
    variation = get_object_or_404(NameVariation, variation_id=variation_id)
    return render(request, "transactions/update_variation.html", {
        'variation': variation
    })

def do_update_variation(request, variation_id):
    if request.method == "POST":
        variation_name = request.POST.get("variation")
        score = request.POST.get("score")
        is_active = request.POST.get("is_active")

        variation = get_object_or_404(NameVariation, variation_id=variation_id)

        variation.variation = variation_name
        variation.score = int(score) if score else 0  # Ensure score is an integer
        variation.is_active = is_active == 'enabled'  # Checkbox for boolean value
        variation.save()

        # Redirect to the view_record with the record_id
        record_id = variation.sanction_record.id
        return redirect("transactions:view_record", record_id=record_id)  # Pass record_id to URL


def add_variation(request, record_id):
    sanction_record = get_object_or_404(SanctionRecord, id=record_id)
    if request.method == "POST":
        variation_name = request.POST.get("variation")
        score = request.POST.get("score")
        is_active = request.POST.get("is_active")

        # Create and save the new variation
        NameVariation.objects.create(
            sanction_record=sanction_record,
            variation=variation_name,
            score=int(score) if score else 0,
            is_active=is_active == 'enabled'  # Checkbox for boolean value
        )

        # Redirect to the view_record with the record_id
        return redirect("transactions:view_record", record_id=record_id)

    return render(request, "transactions/add_variation.html", {
        'sanction_record': sanction_record
    })



def disable_variation(request, variation_id):
    if request.method == 'POST':
        variation = get_object_or_404(NameVariation, variation_id=variation_id)
        variation.is_active = False
        variation.save()

        # Redirect to the view record page
        # Adjust this if necessary to match your URL configuration
        return redirect('transactions:view_record', record_id=variation.sanction_record.id)

    return render(request, 'transactions/disable_variation.html', {'variation_id': variation_id})






#-----------------------------------------------------------------RECORDS & VARIATIONS---------------------------------



def records_variations(request):
    # Get filter parameters from GET request
    watch_list_id = request.GET.get('watch_list_id', '')
    id_original = request.GET.get('id_original', '')
    first_name = request.GET.get('first_name', '')
    last_name = request.GET.get('last_name', '')
    list_name = request.GET.get('list_name', '')

    # Filter records based on provided criteria
    sanction_records = SanctionRecord.objects.all()
    
    if watch_list_id:
        sanction_records = sanction_records.filter(watch_list_id=watch_list_id)
    if id_original:
        sanction_records = sanction_records.filter(id_original=id_original)
    if first_name:
        sanction_records = sanction_records.filter(first_name__icontains=first_name)
    if last_name:
        sanction_records = sanction_records.filter(last_name__icontains=last_name)
    if list_name:
        sanction_records = sanction_records.filter(list_name=list_name)

    # Pagination logic
    paginator = Paginator(sanction_records, 10)  # Show 10 records per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get variation count for each record
    for record in page_obj.object_list:
        record.variation_count = NameVariation.objects.filter(sanction_record_id=record.id).count()

    # Get summary of records by list name
    list_summary = SanctionRecord.objects.values('list_name').annotate(total_records=Count('id')).order_by('list_name')

    # Pass data to the template
    context = {
        'sanction_records': page_obj.object_list,
        'page_obj': page_obj,
        'watch_list_id': watch_list_id,
        'id_original': id_original,
        'first_name': first_name,
        'last_name': last_name,
        'list_name': list_name,
        'list_summary': list_summary,
        'total_records': paginator.count,
    }

    return render(request, 'transactions/records_variations.html', context)






#-----------------------------------------------View Record--------------------------------------------

from uuid import UUID
from django.shortcuts import get_object_or_404, render
from .models import SanctionRecord, NameVariation
from .forms import NameVariationForm
import logging

logger = logging.getLogger(__name__)

from django.shortcuts import render, get_object_or_404
from uuid import UUID
from .models import SanctionRecord, NameVariation
from .forms import NameVariationForm

def view_record(request, record_id, variation_id=None):
    # Convert record_id from string to UUID
    try:
        record_id = UUID(record_id)
    except ValueError:
        # Handle invalid UUID format
        return render(request, '404.html', status=404)
    
    # Retrieve the SanctionRecord instance or return a 404 if not found
    record = get_object_or_404(SanctionRecord, pk=record_id)
    
    # Process aliases if available
    aliases = []
    if record.alias and record.alias_type:
        alias_list = record.alias.split('\n')
        alias_type_list = record.alias_type.split('\n')
        aliases = list(zip(alias_list, alias_type_list))
    
    # Process identity numbers if available
    identities = [
        (item.split(':')[0].strip(), item.split(':')[1].strip())
        for item in (record.identity_numbers.split(', ') if record.identity_numbers else [])
        if ':' in item
    ]
    
    # Retrieve NameVariation instances associated with the SanctionRecord
    variations = NameVariation.objects.filter(sanction_record=record)
    
    # Prepare variations with status and forms for editing
    variations_with_status = [
        {
            'variation_id': variation.variation_id,
            'name': variation.variation,
            'score': variation.score,
            'status': 'Enabled' if variation.is_active else 'Disabled',
            'created_by': 'System',  # Check for created_by
            'form': NameVariationForm(instance=variation)
        }
        for variation in variations
    ]
    
    # Prepare context for rendering the template
    context = {
        'list_name': record.list_name,
        'record': record,
        'aliases': aliases,
        'identities': identities,
        'variations': variations_with_status,
        'full_name': f"{record.first_name} {record.last_name}",
        'country': record.country,  # Add country to context
        'city': record.city,        # Add city to context
    }
    
    # Render the view_record template with the context data
    return render(request, 'transactions/view_record.html', context)





#--------------------------------------------------Variations-----------------------------------------------

from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.shortcuts import render
import uuid

from django.shortcuts import render, redirect, get_object_or_404
from .models import NameVariation, SanctionRecord


def view_variations(request):
    # Initialize variables
    records = SanctionRecord.objects.all()
    data = []

    # Get filtering inputs and selections
    watch_list_id = request.GET.get('watch_list_id', '')
    name_filter = request.GET.get('name', '').strip()
    identity_type_filter = request.GET.get('identity_type', '').strip()
    country_filter = request.GET.get('country', '').strip()

    # Apply filters based on input
    if watch_list_id:
        records = records.filter(watch_list_id=watch_list_id)
    if name_filter:
        records = records.filter(
            Q(first_name__icontains=name_filter) | Q(last_name__icontains=name_filter)
        )
    if identity_type_filter:
        records = records.filter(identity_type__icontains=identity_type_filter)
    if country_filter:
        records = records.filter(country__icontains=country_filter)

    # Fetch records with the count of existing variations
    records = records.annotate(
        variation_count=Count('variations')
    )

    # Generate variations for records with no existing variations
    records_to_generate = records.filter(variation_count=0)
    if records_to_generate.exists():
        combined_names = [f"{record.first_name} {record.last_name}" for record in records_to_generate]
        variations = generate_bulk_name_variations(combined_names)
        
        name_variations_to_create = []
        for record, variations_for_name in zip(records_to_generate, variations):
            if NameVariation.objects.filter(sanction_record=record).exists():
                # Skip creating new variations if they already exist for the record
                continue

            name_variations_to_create.extend(
                NameVariation(
                    sanction_record=record,
                    variation=variation,
                    score=score
                )
                for variation, score in variations_for_name.items()
            )
        
        # Create new name variations in bulk
        if name_variations_to_create:
            NameVariation.objects.bulk_create(name_variations_to_create)

    # Prepare data for rendering
    for record in records:
        combined_name = f"{record.first_name} {record.last_name}"
        variation_count = record.variation_count
        
        variations_list = list(NameVariation.objects.filter(sanction_record=record).values('id', 'variation', 'score'))
        data.append({
            'combined_name': combined_name,
            'entity_type': record.entity_type,
            'created_date': record.created_date,
            'variations': variations_list,
            'variation_count': variation_count,
            'list_name': record.list_name,
            'dataset_id': record.dataset_id,
            'watch_list_id': record.watch_list_id,
        })

    # Paginate data
    paginator = Paginator(data, 10)
    page_number = request.GET.get('10')
    page_obj = paginator.get_page(page_number)

    return render(request, 'transactions/generate_test_data.html', {
        'page_obj': page_obj,
        'show_data': request.GET.get('generate'),  # Whether to show data based on "Generate" button click
        'watch_list_id': watch_list_id,  # Pass the filter parameter to the template
    })


def generate_bulk_name_variations(combined_names):
    # Bulk version of name variations generation
    variations = []
    for name in combined_names:
        name_variations = generate_name_variations(name)
        if isinstance(name_variations, dict):
            variations.append(name_variations)
        else:
            # Log or handle the error if the expected format is not returned
            print(f"Unexpected format for name variations: {name_variations}")
            variations.append({})  # Append an empty dict as a fallback
    return variations




import csv
from django.http import HttpResponse

def export_variations(request):
    # Initialize the HTTP response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="variations_export.csv"'
    
    writer = csv.writer(response)
    
    # Write header row
    writer.writerow([
        'Name', 'Test ID', 'Dataset ID', 'Entity Type', 'List Name', 
        'Variation ID', 'Variation', 'Score', 'Number of Entries', 
        'Filter Option', 'System Option', 'Test Option', 'Complexity Level'
    ])

    # Get filtering inputs and selections
    num_entries = request.GET.get('num_entries', '')
    num_entries = int(num_entries) if num_entries.isdigit() else None
    filter_option = request.GET.get('filter_option', '')
    name_filter = request.GET.get('name', '').strip()
    identity_type_filter = request.GET.get('identity_type', '').strip()
    country_filter = request.GET.get('country', '').strip()
    system_option = request.GET.get('system_option', '')
    test_option = request.GET.get('test_option', '')
    complexity_level = request.GET.get('complexity_level', '')

    # Query records based on filters
    records = SanctionRecord.objects.all()
    if filter_option:
        if filter_option == 'name':
            records = records.filter(first_name__icontains=name_filter) | records.filter(last_name__icontains=name_filter)
        elif filter_option == 'identity_type':
            records = records.filter(identity_type__icontains=identity_type_filter)
        elif filter_option == 'country':
            records = records.filter(country__icontains=country_filter)

    # Limit the records if num_entries is specified
    if num_entries:
        records = records[:num_entries]

    # Loop through the records and write their variations to the CSV file
    for record in records:
        combined_name = f"{record.first_name} {record.last_name}"
        existing_variations = NameVariation.objects.filter(sanction_record=record)
        for variation in existing_variations:
            writer.writerow([
                combined_name,
                variation.test_id,
                record.dataset_id,
                record.entity_type,
                record.list_name,
                variation.variation_id,
                variation.variation,
                variation.score,
                num_entries,
                filter_option,
                system_option,
                test_option,
                complexity_level
            ])
    
    return response



#------------------------------------Data Parsing | Saving to CSV | Show into Model DB--------------------------------------------------------


import xml.etree.ElementTree as ET
import pycountry
import csv
from django.utils.dateparse import parse_datetime
from django.utils.timezone import now
from .models import SanctionRecord, UploadStatistics
import uuid



def parse_ofac_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    namespaces = {
        'ns': 'https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/ENHANCED_XML'
    }

    entities = []

    reference_values = {}
    for ref in root.findall('.//ns:referenceValue', namespaces):
        ref_id = ref.get('refId')
        value_type = ref.find('ns:type', namespaces)
        value_type_text = value_type.text if value_type is not None else ''
        value = ref.find('ns:value', namespaces)
        value_text = value.text if value is not None else ''
        reference_values[ref_id] = value_text

    for entity in root.findall('.//ns:entity', namespaces):
        entity_id = entity.get('id')
        general_info = entity.find('ns:generalInfo', namespaces)
        identity_id = None
        entity_type = None

        if general_info is not None:
            identity_id_elem = general_info.find('ns:identityId', namespaces)
            identity_id = identity_id_elem.text if identity_id_elem is not None else ''

            entity_type_elem = general_info.find('ns:entityType', namespaces)
            entity_type = entity_type_elem.text if entity_type_elem is not None else ''

        names = entity.findall('ns:names/ns:name', namespaces)
        alias = None
        formatted_first_name = None
        formatted_last_name = None

        for name in names:
            is_primary = name.find('ns:isPrimary', namespaces)
            if is_primary is not None and is_primary.text == 'true':
                translations = name.findall('ns:translations/ns:translation', namespaces)
                for translation in translations:
                    is_primary_translation = translation.find('ns:isPrimary', namespaces)
                    if is_primary_translation is not None and is_primary_translation.text == 'true':
                        formatted_first_name_elem = translation.find('ns:formattedFirstName', namespaces)
                        formatted_first_name = formatted_first_name_elem.text if formatted_first_name_elem is not None else ''

                        formatted_last_name_elem = translation.find('ns:formattedLastName', namespaces)
                        formatted_last_name = formatted_last_name_elem.text if formatted_last_name_elem is not None else ''

                        formatted_full_name_elem = translation.find('ns:formattedFullName', namespaces)
                        alias = formatted_full_name_elem.text if formatted_full_name_elem is not None else ''

        city = None
        country = None
        watchlist_country = None

        for address in entity.findall('ns:addresses/ns:address', namespaces):
            primary_translation = address.find('ns:translations/ns:translation[ns:isPrimary="true"]', namespaces)
            if primary_translation is not None:
                for part in primary_translation.findall('ns:addressParts/ns:addressPart', namespaces):
                    part_type = part.find('ns:type', namespaces)
                    if part_type is not None and part_type.text == 'CITY':
                        city = part.find('ns:value', namespaces).text if part.find('ns:value', namespaces) is not None else ''
                        break

                country_elem = address.find('ns:country', namespaces)
                country = country_elem.text if country_elem is not None else ''
                try:
                    watchlist_country = pycountry.countries.get(name=country).alpha_2
                except AttributeError:
                    watchlist_country = ''

        identity_type = None
        identity_number = None

        for document in entity.findall('ns:identityDocuments/ns:identityDocument', namespaces):
            type_elem = document.find('ns:type', namespaces)
            identity_type = type_elem.text if type_elem is not None else ''

            document_number_elem = document.find('ns:documentNumber', namespaces)
            identity_number = document_number_elem.text if document_number_elem is not None else ''

        entity_data = {
            'ID Original': entity_id,
            'List Name': 'Ofac',
            'First Name': formatted_first_name,
            'Last Name': formatted_last_name,
            'Alias Type': 'formattedFullName',
            'Alias': alias,
            'Entity Type': entity_type,
            'Identity Type': identity_type,
            'Identity Number': identity_number,
            'City': city,
            'Country': country,
            'Watchlist Country': watchlist_country
        }

        print(f"Processed OFAC entity: {entity_data}")

        entities.append(entity_data)

    return entities

def save_to_csv(data, csv_file):
    if not data:
        print("No data to write to CSV.")
        return

    keys = data[0].keys()
    with open(csv_file, 'w', newline='', encoding='utf-8') as output_csv:
        dict_writer = csv.DictWriter(output_csv, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)

    print(f"Data has been written to {csv_file}")


def parse_eu_xml(xml_file):
    context = ET.iterparse(xml_file, events=("start", "end"))
    ns = None
    data = []

    for event, elem in context:
        if event == "start" and ns is None:
            ns = {'ns': elem.tag.split('}')[0].strip('{')}

        if event == "end" and elem.tag.endswith('nameAlias'):
            logical_id = elem.get('logicalId', '')
            first_name = elem.get('firstName', '')
            last_name = elem.get('lastName', '')
            whole_name = elem.get('wholeName', '')
            city = elem.get('city', '')
            country = elem.get('country', '')
            alias_type = 'Whole Name'
            entity_type = get_entity_type(elem, logical_id, ns)
            identity_types_str = ', '.join([identity_type for identity_type in get_identity_types(whole_name)])
            identity_numbers = ', '.join([identity_number for identity_number in get_identity_numbers(whole_name)])
            watchlist_country = get_watchlist_country(elem, logical_id, ns)

            data.append({
                'First Name': first_name,
                'Last Name': last_name,
                'List Name': 'EU',
                'City': city,
                'Country': country,
                'Watchlist Country': watchlist_country,
                'ID Original': logical_id,
                'Entity Type': entity_type,
                'Identity Type': identity_types_str,
                'Identity Number': identity_numbers,
                'Alias': whole_name,
                'Alias Type': alias_type
            })

            elem.clear()

    return data

def get_identity_types(whole_name):
    identity_types = {
        'Passport': '',
        'SSN': '',
        'National ID No': '',
        'Driver\'s License No.': '',
        'Registration ID': '',
        'Vessel Registration Identification': '',
        'Italian Fiscal Code': '',
        'Company Number': ''
    }
    for identity_type in identity_types.keys():
        if identity_type.lower() in whole_name.lower():
            identity_types[identity_type] = whole_name
    return [k for k, v in identity_types.items() if v]

def get_identity_numbers(whole_name):
    return [whole_name] if whole_name else []

def get_entity_type(elem, logical_id, ns):
    try:
        xpath_expr = f".//YourElement[@logicalId='{logical_id}']"
        sanction_entities = elem.findall(xpath_expr, namespaces=ns)
        if sanction_entities:
            for entity in sanction_entities:
                return entity.get('type', '')
    except Exception:
        return ''
    return ''

def get_watchlist_country(elem, logical_id, ns):
    watchlist_country = ''
    xpath_expr = f".//ns:watchlistCountry[ns:nameAlias[@logicalId='{logical_id}']]"
    try:
        countries = elem.findall(xpath_expr, ns)
        if countries:
            for country in countries:
                return country.get('country', '')
    except Exception:
        pass
    return watchlist_country

def save_to_csv(data, csv_file):
    if not data:
        print("No data to write to CSV.")
        return

    keys = data[0].keys()
    with open(csv_file, 'w', newline='', encoding='utf-8') as output_csv:
        dict_writer = csv.DictWriter(output_csv, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)

    print(f"Data has been written to {csv_file}")


#-------------------------------------------PROCESSING CSV TO MODEL----------------------------------



import uuid
from django.core.exceptions import ValidationError

import logging

logger = logging.getLogger(__name__)

def generate_and_print_name_variations(record):
    try:
        # Ensure 'ID Original' is mapped correctly and the record exists
        try:
            sanction_record = SanctionRecord.objects.get(id_original=record.get('ID Original'))
        except SanctionRecord.DoesNotExist:
            logger.warning(f"SanctionRecord with ID Original {record.get('ID Original')} does not exist. Skipping variations.")
            return
        
        # Determine the name fields to use for generating variations
        first_name = record.get('First Name', '').strip()
        last_name = record.get('Last Name', '').strip()
        formatted_name = record.get('Formatted Name', '').strip()

        if not first_name and not last_name:
            if formatted_name:
                name_to_use = formatted_name
            else:
                logger.warning(f"Record {record.get('ID Original')} does not have a first name, last name, or formatted name. Skipping...")
                return
        else:
            name_to_use = f"{first_name} {last_name}".strip()

        # Generate variations
        variations = [
            {'variation': name_to_use, 'score': 0.9, 'variation_id': str(uuid.uuid4())},
            # Add other variation logic here (e.g., phonetic, prefix/suffix, etc.)
        ]

        # Store variations in the database and print them to the terminal
        for variation in variations:
            NameVariation.objects.create(
                sanction_record_id=sanction_record.id,
                variation=variation['variation'],
                score=variation['score'],
                variation_id=variation['variation_id']
            )
            # Print the variation to the terminal
            print(f"Generated Variation: {variation['variation']}, Score: {variation['score']}, Variation ID: {variation['variation_id']}")

    except Exception as e:
        logger.error(f"Error generating variations for record {record}: {e}")

import threading
from django.db import transaction
from django.utils import timezone

import uuid
import time
import threading
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from .models import SanctionRecord, UploadStatistics

def calculate_file_hash(file):
    import hashlib
    file.seek(0)
    file_hash = hashlib.sha256(file.read()).hexdigest()
    file.seek(0)  # Reset file pointer
    return file_hash


import subprocess
import os
import time
import uuid
from django.utils import timezone
from django.db import transaction
from django.core.management import call_command
from .models import SanctionRecord, UploadStatistics

def process_and_save_file(file, list_name):
    output_csv = f'{list_name}_output.csv'
    
    # Start timing the overall process
    start_time = time.time()

    # Handle XML to CSV conversion
    if list_name == 'Ofac':
        data = parse_ofac_xml(file)
    elif list_name == 'EU':
        data = parse_eu_xml(file)
    elif list_name == 'UN':
        xml_data = file.read().decode('utf-8')
        import_xml_to_csv(xml_data, output_csv)
        data = read_csv_to_dict(output_csv)
    else:
        print(f"Unknown list name: {list_name}")
        return 0, 0, 0, output_csv

    if not data:
        print(f"No data found for list: {list_name}")
        return 0, 0, 0, output_csv

    dataset_id = str(uuid.uuid4())
    file_hash = calculate_file_hash(file)

    if UploadStatistics.objects.filter(file_hash=file_hash).exists():
        print(f"File with hash {file_hash} has already been processed. Skipping...")
        return 0, 0, SanctionRecord.objects.count(), output_csv

    records_to_create = []
    records_to_update = []
    records_added = 0
    records_updated = 0

    start_time_db = timezone.now()

    existing_records = SanctionRecord.objects.filter(dataset_id=dataset_id).values('id_original', 'id')
    existing_records_map = {record['id_original']: record['id'] for record in existing_records}

    for record in data:
        try:
            id_original = record.get('ID Original', '')
            record_id = id_original
            first_name = record.get('First Name', '')
            last_name = record.get('Last Name', '')
            entity_type = record.get('Entity Type', 'Unknown')
            identity_numbers = record.get('Identity Number', '')
            identity_types = record.get('Identity Type', '')
            city = record.get('City', 'Unknown')
            country = record.get('Country', 'Unknown')
            watchlist_country = record.get('Watchlist Country', 'Unknown')
            alias = record.get('Alias', '')
            alias_type = record.get('Alias Type', 'Whole Name')

            if record_id in existing_records_map:
                existing_record_id = existing_records_map[record_id]
                existing_record = SanctionRecord.objects.get(pk=existing_record_id)

                needs_update = (
                    existing_record.first_name != first_name or
                    existing_record.last_name != last_name or
                    existing_record.entity_type != entity_type or
                    existing_record.identity_numbers != identity_numbers or
                    existing_record.identity_types != identity_types or
                    existing_record.city != city or
                    existing_record.country != country or
                    existing_record.watchlist_country != watchlist_country or
                    existing_record.alias != alias or
                    existing_record.alias_type != alias_type
                )

                if needs_update:
                    existing_record.first_name = first_name
                    existing_record.last_name = last_name
                    existing_record.entity_type = entity_type
                    existing_record.identity_numbers = identity_numbers
                    existing_record.identity_types = identity_types
                    existing_record.city = city
                    existing_record.country = country
                    existing_record.watchlist_country = watchlist_country
                    existing_record.alias = alias
                    existing_record.alias_type = alias_type
                    existing_record.dataset_id = dataset_id

                    records_to_update.append(existing_record)
                    records_updated += 1

            else:
                new_record = SanctionRecord(
                    id_original=id_original,
                    first_name=first_name,
                    last_name=last_name,
                    entity_type=entity_type,
                    identity_numbers=identity_numbers,
                    identity_types=identity_types,
                    city=city,
                    country=country,
                    watchlist_country=watchlist_country,
                    alias=alias,
                    alias_type=alias_type,
                    dataset_id=dataset_id,
                    created_date=timezone.now()  # Make sure this field is updated
                )
                records_to_create.append(new_record)
                records_added += 1

        except Exception as e:
            print(f"Error processing record {record}: {e}")

    # Perform bulk operations within a transaction
    with transaction.atomic():
        if records_to_create:
            SanctionRecord.objects.bulk_create(records_to_create, batch_size=1000)
        if records_to_update:
            SanctionRecord.objects.bulk_update(records_to_update, fields=[
                'first_name', 'last_name', 'entity_type', 'identity_numbers',
                'identity_types', 'city', 'country', 'watchlist_country',
                'alias', 'alias_type', 'dataset_id'
            ], batch_size=1000)

    end_time_db = timezone.now()
    end_time = time.time()

    total_active_records = SanctionRecord.objects.count()

    UploadStatistics.objects.create(
        list_name=list_name,
        file_hash=file_hash,
        last_import_date=end_time_db,
        records_added=records_added,
        records_updated=records_updated,
        records_deleted=0,
        total_active_records=total_active_records,
        start_time=start_time_db,
        end_time=end_time_db
    )

    # Call the generate_variations management command
    try:
        call_command('generate_variations')  # Ensure 'generate_variations' is the correct command name
    except Exception as e:
        print(f"Error executing generate_variations command: {e}")

    return records_added, records_updated, total_active_records, output_csv






def read_csv_to_dict(csv_file_path):
    with open(csv_file_path, mode='r', newline='', encoding='utf-8') as csv_file:
        return list(csv.DictReader(csv_file))




#-------------------------------------FILE UPLOADING-----------------------------------

def upload_file(request):
    message = ''
    statistics = UploadStatistics.objects.all()
    if request.method == 'POST':
        file = request.FILES.get('xml_file')
        if file:
            if 'process_ofac' in request.POST:
                list_name = 'Ofac'
            elif 'process_eu' in request.POST:
                list_name = 'EU'
            elif 'process_un' in request.POST:
                list_name = 'UN'
            else:
                message = "No valid process selected."
                return render(request, 'transactions/upload.html', {'message': message, 'statistics': statistics})

            records_added, records_updated, total_active_records, output_csv = process_and_save_file(file, list_name)
            message = f"{list_name.upper()} file processed successfully. Records Added: {records_added}, Updated: {records_updated}, Total Active: {total_active_records}. CSV saved as {output_csv}."
        else:
            message = "No file uploaded."
 
    return render(request, 'transactions/upload.html', {'message': message, 'statistics': statistics})



#------------------------------------------------XML TO CSV------------------------------------------------

def import_xml_to_csv(xml_data: str, csv_file_path: str):
    # Parse the XML data from the string
    root = ET.fromstring(xml_data)
    
    # Define the CSV file headers
    csv_headers = [
        'First Name', 'Last Name', 'List Name', 'City', 'Country', 
        'Watchlist Country', 'ID Original', 'Entity Type', 'Identity Type', 
        'Identity Number', 'Alias', 'Alias Type'
    ]

    # Open a CSV file to write the extracted data
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        
        # Write the headers to the CSV file
        csv_writer.writerow(csv_headers)
        
        # Function to process aliases
        def process_aliases(aliases, alias_tag):
            alias_list = []
            for alias in aliases:
                alias_name = alias.findtext("ALIAS_NAME", default="")
                alias_type = alias_tag  # Use the provided alias tag as alias type
                if alias_name:
                    alias_list.append((alias_name, alias_type))
            return alias_list

        # Process each individual
        for individual in root.findall(".//INDIVIDUAL"):
            first_name = individual.findtext("FIRST_NAME", default="")
            last_name = individual.findtext("SECOND_NAME", default="")
            city = individual.findtext(".//ADDRESS/CITY", default="")
            country = individual.findtext(".//NATIONALITY/COUNTRY", default="")
            watchlist_country = individual.findtext(".//ADDRESS/COUNTRY", default="")
            logical_id = individual.findtext("DATAID", default="")
            entity_type = "individual"

            # Extract identity type and number
            identity_types = []
            identity_numbers = []
            for identity in individual.findall(".//INDIVIDUAL_DOCUMENT"):
                identity_type = identity.findtext("TYPE_OF_DOCUMENT", default="")
                identity_number = identity.findtext("NUMBER", default="")
                if identity_type:
                    identity_types.append(identity_type)
                if identity_number:
                    identity_numbers.append(identity_number)

            # Process aliases
            aliases = process_aliases(individual.findall(".//INDIVIDUAL_ALIAS"), "INDIVIDUAL_ALIAS")

            # Write the information for each alias
            for alias_name, alias_type in aliases:
                csv_writer.writerow([
                    first_name, last_name, 'UN', city, country, watchlist_country, 
                    logical_id, entity_type, ', '.join(identity_types), 
                    ', '.join(identity_numbers), alias_name, alias_type
                ])
        
        # Process each entity
        for entity in root.findall(".//ENTITY"):
            first_name = entity.findtext("FIRST_NAME", default="")
            last_name = ""  # Entities typically don't have a last name
            city = entity.findtext(".//ENTITY_ADDRESS/CITY", default="")
            country = entity.findtext(".//ENTITY_ADDRESS/COUNTRY", default="")
            watchlist_country = entity.findtext(".//ENTITY_ADDRESS/COUNTRY", default="")
            logical_id = entity.findtext("DATAID", default="")
            entity_type = "entity"

            # Process aliases
            aliases = process_aliases(entity.findall(".//ENTITY_ALIAS"), "ENTITY_ALIAS")

            # Write the information for each alias
            for alias_name, alias_type in aliases:
                csv_writer.writerow([
                    first_name, last_name, 'UN', city, country, watchlist_country, 
                    logical_id, entity_type, '',  # Identity Type is not applicable to entities
                    '',  # Identity Number is not applicable to entities
                    alias_name, alias_type
                ])




def parse_date(date_str):
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        print(f"Invalid date format: {date_str}")
        return None


