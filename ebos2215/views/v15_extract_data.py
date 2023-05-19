import os
import re
from datetime import datetime
from pathlib import Path

# modules used for extracting eid data
import easyocr
import pdf2image

# module used for extrcting rta vehicle data
import pdfplumber
from django.contrib import messages
from django.core.files.base import ContentFile

# modules used for saving uploaded file in media root
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from PyPDF2 import PdfFileReader

from ..models import (
    T15rpa_drvlic_data,
    T15rpa_eid_data,
    T15rpa_policy_data,
    T15rpa_vehreg_data,
)

# getting media Directory path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
PDF_DIR = Path.joinpath(BASE_DIR, "documents")

poppler_path = str(Path(BASE_DIR)) + "\poppler-0.68.0\\bin"

# Create your views here.
def extractdata(request):
    return render(request, "t15_extract_data.html")


def fileuploaded(pdf_file, doctype):
    file_format = pdf_file.name
    file_type = file_format.split(".")[1]
    fullpath = str(Path(PDF_DIR)) + "\\" + str(pdf_file)
    if file_type == "pdf":
        pdf = PdfFileReader(fullpath)
    if doctype == "D":
        if file_type == "pdf":
            # converting pdf to image poppler_path is manadatory when using windows
            img_file = pdf2image.convert_from_path(
                fullpath, 500, poppler_path=poppler_path
            )
            image_counter1 = 1
            img_name = "test"

            for page in img_file:
                filename1 = img_name + str(image_counter1) + ".jpg"
                page.save(filename1, "JPEG")
                values = licenseData(filename1)
                image_counter1 = image_counter1 + 1
                if os.path.exists(filename1):
                    os.remove(filename1)
                else:
                    print("Can not delete the file as it doesn't exists")
        else:
            fullpath = str(Path(PDF_DIR)) + "\\" + str(pdf_file)
            values = licenseData(fullpath)

        license = values.get("license")
        name = values.get("name")
        nationality = values.get("nationality")
        date_of_birth = datetime.strptime(
            values.get("date_of_birth"), "%d-%m-%Y"
        ).strftime("%Y-%m-%d")
        issue_date = datetime.strptime(values.get("issue_date"), "%d-%m-%Y").strftime(
            "%Y-%m-%d"
        )
        expiry_date = datetime.strptime(values.get("expiry_date"), "%d-%m-%Y").strftime(
            "%Y-%m-%d"
        )
        place_of_issue = values.get("place_of_issue")

        # saving data in respective driving table
        drivingLicense = T15rpa_drvlic_data(
            license=license,
            name=name,
            nationality=nationality,
            date_of_birth=date_of_birth,
            issue_date=issue_date,
            expiry_date=expiry_date,
            place_of_issue=place_of_issue,
        )
        drivingLicense.save()

        successPage = (
            "/admin/ebos2215/t15rpa_drvlic_data/" + str(drivingLicense.id) + "/change/"
        )
        # messages.success(request,"Records added successfully!")
        return successPage
    # saved rta vehicle license data
    if doctype == "R":
        values = rtaData(fullpath)

        traffic_plate = values.get("traffic_plate")
        place_of_issue = values.get("place_of_issue")
        plate_cls = values.get("plate_cls")
        traffic_code = values.get("traffic_code")
        owner = values.get("owner")
        ins_expiry = datetime.strptime(values.get("ins_expiry"), "%d/%m/%Y").strftime(
            "%Y-%m-%d"
        )
        nationality = values.get("nationality")
        policy_no = values.get("policy_no")
        reg_date = datetime.strptime(values.get("reg_date"), "%d/%m/%Y").strftime(
            "%Y-%m-%d"
        )
        ins_type = values.get("ins_type")
        expiry_date = datetime.strptime(values.get("expiry_date"), "%d/%m/%Y").strftime(
            "%Y-%m-%d"
        )
        passenger_no = values.get("passenger_no")
        year_model = values.get("year_model")
        origin = values.get("origin")
        vehicle_clr = values.get("vehicle_clr")
        vehicle_clss = values.get("vehicle_clss")
        vehicle_type = values.get("vehicle_type")
        empty_weight = values.get("empty_weight")
        gross_weight = values.get("gross_weight")
        engine_no = values.get("engine_no")
        chasis_no = values.get("chasis_no")

        # saving data in respective rta table
        rta = T15rpa_vehreg_data(
            traffic_plate=traffic_plate,
            place_of_issue=place_of_issue,
            plate_cls=plate_cls,
            traffic_code=traffic_code,
            owner=owner,
            ins_expiry=ins_expiry,
            nationality=nationality,
            policy_no=policy_no,
            reg_date=reg_date,
            ins_type=ins_type,
            expiry_date=expiry_date,
            passenger_no=passenger_no,
            year_model=year_model,
            origin=origin,
            vehicle_clr=vehicle_clr,
            vehicle_clss=vehicle_clss,
            vehicle_type=vehicle_type,
            empty_weight=empty_weight,
            gross_weight=gross_weight,
            engine_no=engine_no,
            chasis_no=chasis_no,
        )
        rta.save()
        successPage = "/admin/ebos2215/t15rpa_vehreg_data/" + str(rta.id) + "/change/"
        # messages.success('POST', "Records added successfully!")
        return successPage
    if doctype == "E":

        totalpages = pdf.numPages

        # convert to jpg file after uploading
        img_file = pdf2image.convert_from_path(fullpath, 500, poppler_path=poppler_path)

        image_counter1 = 1
        img_name = "test"
        values = {}
        id_num = ""
        name = ""
        nationality = ""
        sex = ""
        date_of_birth = ""
        expiry_date = ""
        card_num = ""

        for page in img_file:
            filename1 = img_name + str(image_counter1) + ".jpg"
            page.save(filename1, "JPEG")
            values = eidData(filename1, image_counter1, totalpages)
            if totalpages > 1:
                if image_counter1 == 1:
                    id_num = values.get("id_num")
                    name = values.get("name")
                    nationality = values.get("nationality")
                else:
                    if image_counter1 == 2:
                        sex = values.get("sex")
                        date_of_birth = datetime.strptime(
                            values.get("date_of_birth"), "%d/%m/%Y"
                        ).strftime("%Y-%m-%d")
                        expiry_date = datetime.strptime(
                            values.get("expiry_date"), "%d/%m/%Y"
                        ).strftime("%Y-%m-%d")
                        card_num = values.get("card_num")
            else:
                id_num = values.get("id_num")
                name = values.get("name")
                nationality = values.get("nationality")
                sex = values.get("sex")
                date_of_birth = datetime.strptime(
                    values.get("date_of_birth"), "%d/%m/%Y"
                ).strftime("%Y-%m-%d")
                expiry_date = datetime.strptime(
                    values.get("expiry_date"), "%d/%m/%Y"
                ).strftime("%Y-%m-%d")
                card_num = values.get("card_num")

            image_counter1 = image_counter1 + 1
            if os.path.exists(filename1):
                os.remove(filename1)
            else:
                print("Can not delete the file as it doesn't exists")
            # os.remove(filename1 )
        # Saving data in Respective EID table
        eid = T15rpa_eid_data(
            id_num=id_num,
            name=name,
            nationality=nationality,
            sex=sex,
            date_of_birth=date_of_birth,
            expiry_date=expiry_date,
            card_num=card_num,
        )
        eid.save()

        successPage = "/admin/ebos2215/t15rpa_eid_data/" + str(eid.id) + "/change/"
        return successPage

    if doctype == "P":
        text = ""
        for page in pdf.pages:
            text += page.extractText()
        x = re.split("\n", text)
        policy_type = x[11]
        docType = x[0]
        policyNo = x[12]
        tcfNo = x[27]
        name = x[40]
        phone = x[64]
        inceptionDate = x[41]
        inceptionDate = datetime.strptime(inceptionDate, "%d/%m/%Y").strftime(
            "%Y-%m-%d"
        )

        expiryDate = x[42]
        expiryDate = datetime.strptime(expiryDate, "%d/%m/%Y").strftime("%Y-%m-%d")
        vehicle = x[108]
        chassisNo = x[109]
        engineNo = x[110]
        regNo = x[116]
        purposeUse = x[145]
        bodyType = x[146]
        manufacYear = x[148]
        seatingCapacity = x[149]
        color = x[159]
        cylinder = x[150]
        premium = x[157]
        insured = x[156]
        policy = T15rpa_policy_data(
            policy_type=policy_type,
            document_type=docType,
            policy_number=policyNo,
            tcf_number=tcfNo,
            name=name,
            phone=phone,
            inception_date=inceptionDate,
            expiryDate=expiryDate,
            vehicle=vehicle,
            chasis_number=chassisNo,
            engine_number=engineNo,
            reg_Number=regNo,
            Purpose_of_use=purposeUse,
            body_type=bodyType,
            manufacture_year=manufacYear,
            seating_capacity=seatingCapacity,
            color=color,
            cylinder=cylinder,
            premium=premium,
            sum_insured=insured,
        )
        policy.save()

        successPage = (
            "/admin/ebos2215/t15rpa_policy_data/" + str(policy.id) + "/change/"
        )
        return successPage


def eidData(filename1, image_counter1, totalpages):
    image_data = filename1
    reader = easyocr.Reader(["en", "ar"])
    img_text = reader.readtext(filename1)
    final_text = ""
    for _, text, __ in img_text:
        final_text += " "
        final_text += text
    text = final_text
    # extracting index values
    id_index = text.find("ID N")
    name_index = text.find("Name")
    nation_index = text.find("Nationality")
    sex_index = text.find("Sex")
    birth = text.find("Date Of")
    if birth == -1:
        birth_index = text.find("Date of")
        if birth_index == -1:
            birth_index = text.find("Date oF")
    else:
        birth_index = birth
    sign_index = text.find("Signature")
    expiry_index = text.find("Expiry Date")
    other_index = text.find("Card Number")
    card_index = text.find("If")

    id_num = ""
    name = ""
    nationality = ""
    sex = ""
    date_of_birth = ""
    expiry_date = ""
    card_num = ""

    if totalpages > 1:
        if image_counter1 == 1:
            if id_index != -1:
                if name_index != -1:
                    id_num = " ".join(
                        re.findall(r"\d[0-9\-]*", text[id_index : name_index - 1])
                    )
                else:
                    id_num = " ".join(
                        re.findall(r"\d[0-9\-]*", text[id_index : nation_index - 1])
                    )
                    name = " ".join(
                        re.findall("[a-zA-Z]+", text[id_index : nation_index - 1])
                    )
                    name = name.split("ID Number", 1)[1]
            else:
                id_num = None

            if name_index != -1:
                name = " ".join(
                    re.findall("[a-zA-Z]+", text[name_index : nation_index - 1])
                )
                name = name.split("Name", 1)[1]

            if nation_index != -1:
                nationalies = " ".join(re.findall("[a-zA-Z]+", text[nation_index:]))
                nationality = nationalies.split("Nationality ", 1)[1]
            else:
                nationality = None

        if image_counter1 == 2:
            sex_index = text.find("Sex")
            birth = text.find("Date Of")
            if birth == -1:
                birth_index = text.find("Date of")
                if birth_index == -1:
                    birth_index = text.find("Date oF")
            else:
                birth_index = birth
            sign_index = text.find("Signature")
            expiry_index = text.find("Expiry Date")
            other_index = text.find("Card Number")
            card_index = text.find("If")

            if sex_index != -1:
                sexx = " ".join(
                    re.findall("[a-zA-Z]+", text[sex_index : birth_index - 1])
                )
                sex = sexx.split("Sex ", 1)[1]

            else:
                sex = None

            if birth_index != -1:
                date = text[birth_index : sign_index - 1]
                date_of_birth = " ".join(re.findall(r"\d[0-9\\]*", date)).replace(
                    " ", "/"
                )
            else:
                date_of_birth = None

            if other_index != -1:
                other_details = " ".join(
                    re.findall(r"\d[0-9\\]*", text[other_index : card_index - 1])
                )
                expiry_date = other_details[0:10].replace(" ", "/")
                card_num = other_details[11:20]
            else:
                expiry_date = None
                card_num = None

    else:

        # extracting values
        if id_index != -1:
            id_num = " ".join(
                re.findall(r"\d[0-9\-]*", text[id_index : name_index - 1])
            )
        else:
            id_num = None

        if name_index != -1:
            name = " ".join(
                re.findall("[a-zA-Z]+", text[name_index : nation_index - 1])
            )
            name = name.split("Name", 1)[1]

        else:
            name = None
        if name == None:
            name = " ".join(re.findall("[a-zA-Z]+", text[id_index : nation_index - 1]))
            name = name.split("ID Number")

        if nation_index != -1:
            nationalies = " ".join(
                re.findall("[a-zA-Z]+", text[nation_index : sex_index - 1])
            )
            nationality = nationalies.split("Nationality ", 1)[1]
        else:
            nationality = None

        if sex_index != -1:
            sexx = " ".join(re.findall("[a-zA-Z]+", text[sex_index : birth_index - 1]))
            sex = sexx.split("Sex ", 1)[1]

        else:
            sex = None

        if birth_index != -1:
            date = text[birth_index : sign_index - 1]
            date_of_birth = " ".join(re.findall(r"\d[0-9\\]*", date)).replace(" ", "/")
        else:
            date_of_birth = None

        if other_index != -1:
            other_details = " ".join(
                re.findall(r"\d[0-9\\]*", text[other_index : card_index - 1])
            )
            expiry_date = other_details[0:10].replace(" ", "/")
            card_num = other_details[11:20]
        else:
            expiry_date = None
            card_num = None

    params = {
        "id_num": id_num,
        "name": name,
        "nationality": nationality,
        "sex": sex,
        "date_of_birth": date_of_birth,
        "expiry_date": expiry_date,
        "card_num": card_num,
    }

    return params


def licenseData(filename1):
    image_data = filename1
    reader = easyocr.Reader(["en", "ar"])
    img_text = reader.readtext(image_data)
    final_text = ""
    for _, text, __ in img_text:
        final_text += " "
        final_text += text
    text = final_text
    license_num = ""
    names = ""
    nationality = ""
    date_of_birth = ""
    issue_date = ""
    expiry_date = ""
    place_of_issue = ""
    # extracting index values
    license = text.find("License")
    if license == -1:
        license_index = text.find("Iirivag")
        if license_index == -1:
            license_index = text.find("Iirivg")
    else:
        license_index = license
    name_index = text.find("Name")

    nationality = text.find("Nationality")
    if nationality == -1:
        nationality_index = text.find("Mauionality")
    else:
        nationality_index = nationality
    dob = text.find("Date of")
    if dob == -1:
        dob_index = text.find("Dulul")
        if dob_index == -1:
            dob_index = text.find("Dutu")
    else:
        dob_index = dob
    issue_index = text.find("Issue Date")

    expiry = text.find("Expiry")
    if expiry == -1:
        expiry_index = text.find("Enpiry")
        if expiry_index == -1:
            expiry_index = text.find("Brniry")
    else:
        expiry_index = expiry
    poi = text.find("Place")
    if poi == -1:
        poi_index = text.find("Plac")
        if poi_index == -1:
            poi_index = text.find("?????")
    else:
        poi_index = poi

    traffic = text.find("Traffic")

    if license_index != -1:
        license = text[license_index : nationality_index - 1]
        license_no = " ".join(re.findall(r"\d[0-9\-]*", license))
        license_num = license_no.split(" ")[-1]
    else:
        license_num = None

    if name_index != -1:
        name_val = text[name_index : nationality_index - 1]
        # name_val = " ".join(re.findall("[a-zA-Z]+", license))
        names = name_val.split("Name ", 1)[1]

    else:

        name = " ".join(re.findall("[a-zA-Z]+", license))
        if "License" in name:
            names = name.split("License ", 1)[1]
        else:
            names = name.split("Iirivag ", 1)[1]

    if nationality_index != -1:
        nationality_num = text[nationality_index : dob_index - 1]
        nation = " ".join(re.findall("[a-zA-Z]+", nationality_num))
        if "Nationality" in nation:
            nationality = nation.split("Nationality ", 1)[1]
        else:
            nationality = nation.split("Mauionality ", 1)[1]
    else:
        nationality = None

    if dob_index != -1:
        dob_num = text[dob_index : expiry_index - 1]
        dob = re.findall(r"\d[0-9\-]*", dob_num)
        if len(dob[0]) == 1:
            date_of_birth = dob[1]
            dbval = date_of_birth.split("-")
            if len(dbval) == 2:
                dob1 = dbval[0] + "-"
                dob2 = dbval[1]
                latest_dob = dob2.replace(dob2[2], "-")
                date_of_birth = dob1 + latest_dob

        else:
            date_of_birth = dob[0]

        if issue_index == -1:
            issue_date = "".join(dob[-2:])
        else:
            if issue_index != -1:
                issue_date = text[issue_index : expiry_index - 1]
                issue_date = " ".join(re.findall(r"\d[0-9\-]*", issue_date))
            else:
                issue_date = None

    else:
        date_of_birth = None

    if expiry_index != -1:
        expiry_num = text[expiry_index : poi_index - 1]
        expiry = " ".join(re.findall(r"\d[0-9\-]*", expiry_num))
        expiry_date = expiry.split(" ", 1)[0]
    else:
        expiry_date = None
    if poi_index != -1:
        if traffic != -1:
            place_of_issue = text[poi_index : traffic - 1]
        else:
            place_of_issue = text[poi_index:]
    else:
        place_of_issue = None

    place = place_of_issue

    poi_value = " ".join(re.findall("[a-zA-Z]+", place))
    if "Plac" in poi_value:
        place_of_issue = poi_value.split(" ")[1]
    if "Placa of Issue " in poi_value:
        place = poi_value.split("Placa of Issue ", 1)[1]
        place_of_issue = place.split(" ")[0]

    params = {
        "license": license_num,
        "name": names,
        "nationality": nationality,
        "date_of_birth": date_of_birth,
        "issue_date": issue_date,
        "expiry_date": expiry_date,
        "place_of_issue": place_of_issue,
    }

    return params


def rtaData(filename1):
    text = ""
    with pdfplumber.open(filename1) as pdf:
        first_page = pdf.pages[0]
        text = first_page.extract_text()
    if text == "":
        values = rtaScannedData(filename1)
        traffic_plate = values.get("traffic_plate")
        place_of_issue = values.get("place_of_issue")
        plate_cls = values.get("plate_cls")
        traffic_code = values.get("traffic_code")
        owner = values.get("owner")
        ins_expiry = values.get(
            "ins_expiry"
        )  # datetime.strptime(values.get('ins_expiry'),"%d/%m/%Y").strftime("%Y-%m-%d")
        nationality = values.get("nationality")
        policy_no = values.get("policy_no")
        reg_date = values.get(
            "reg_date"
        )  # datetime.strptime(values.get('reg_date'), '%d/%m/%Y').strftime("%Y-%m-%d")
        ins_type = values.get("ins_type")
        expiry_date = values.get(
            "expiry_date"
        )  # datetime.strptime(values.get('expiry_date'), '%d/%m/%Y').strftime("%Y-%m-%d")
        passenger_no = values.get("passenger_no")
        year_model = values.get("year_model")
        origin = values.get("origin")
        vehicle_clr = values.get("vehicle_clr")
        vehicle_clss = values.get("vehicle_clss")
        vehicle_type = values.get("vehicle_type")
        empty_weight = values.get("empty_weight")
        gross_weight = values.get("gross_weight")
        engine_no = values.get("engine_no")
        chasis_no = values.get("chasis_no")

    else:
        # Extracting Index values of  vehicle license
        tp_idx = text.find("Traffic plate")
        poi_idx = text.find("Place of issue")
        pc_idx = text.find("Plate class")
        tc_idx = text.find("Traffic Code No")
        owner_idx = text.find("Owner")

        ins_idx = text.find("Insurance Expiry")
        natl_idx = text.find("Nationality")
        policy_idx = text.find("Policy No")
        reg_idx = text.find("Registration Date")
        instype_idx = text.find("Insurance Type")
        exp_idx = text.find("Expiry Date")
        mortage_idx = text.find("Mortgaged")

        # Extracting Index values of  vehicle info
        pax_idx = text.find("No. of passengers")
        model_idx = text.find("Year model")
        orgin_idx = text.find("Origin")
        clr_idx = text.find("Vehicle color")
        cls_idx = text.find("Vehicle class")
        type_idx = text.find("Vehicle type")
        empt_idx = text.find("Empty weight")
        grs_idx = text.find("Gross vehicle weight")
        engine_idx = text.find("Engine No")
        chasis_idx = text.find("Chassis No")
        rmrks_idx = text.find("Remarks")

        # extracting data from index values
        if tp_idx != -1:
            tpval = text[tp_idx : poi_idx - 1].split(":")
            traffic_plate = tpval[1]

        else:
            traffic_plate = None

        if poi_idx != -1:
            tpval = text[poi_idx : pc_idx - 1].split(":")[1]
            place_of_issue = " ".join(re.findall("[a-zA-Z]+", tpval))

        else:
            place_of_issue = None

        if pc_idx != -1:
            pcval = text[pc_idx : tc_idx - 1].split(":")[1]
            plate_cls = " ".join(re.findall("[a-zA-Z]+", pcval))

        else:
            plate_cls = None

        if tc_idx != -1:
            tcval = text[tc_idx : owner_idx - 1].split(":")
            traffic_code = tcval[1]

        else:
            traffic_code = None

        if owner_idx != -1:
            onrval = text[owner_idx : ins_idx - 1]
            owner = " ".join(re.findall("[a-zA-Z]+", onrval))

        else:
            owner = None

        if ins_idx != -1:
            insval = text[ins_idx : natl_idx - 1].split(":")
            ins_expiry = insval[1].strip()

        else:
            ins_expiry = None

        if natl_idx != -1:
            natlval = text[natl_idx : policy_idx - 1].split(":")[1]
            nationality = " ".join(re.findall("[a-zA-Z]+", natlval))

        else:
            nationality = None

        if policy_idx != -1:
            polval = text[policy_idx : reg_idx - 1].split(":")
            policy_no = polval[1]

        else:
            policy_no = None

        if reg_idx != -1:
            regval = text[reg_idx : instype_idx - 1].split(":")
            reg_date = insval[1].strip()

        else:
            reg_date = None

        if instype_idx != -1:
            insval = text[instype_idx : exp_idx - 1].split(":")[1]
            ins_type = " ".join(re.findall("[a-zA-Z]+", insval))

        else:
            ins_type = None

        if exp_idx != -1:
            expval = text[exp_idx : mortage_idx - 1].split(":")
            expiry_date = expval[1].strip()

        else:
            expiry_date = None

        if pax_idx != -1:
            paxval = text[pax_idx : model_idx - 1].split(":")
            passenger_no = paxval[1]

        else:
            passenger_no = None

        if model_idx != -1:
            modelval = text[model_idx : orgin_idx - 1].split(":")
            year_model = modelval[1]

        else:
            year_model = None

        if orgin_idx != -1:
            orgval = text[orgin_idx : clr_idx - 1].split(":")[1]
            origin = " ".join(re.findall("[a-zA-Z]+", orgval))

        else:
            origin = None

        if clr_idx != -1:
            clrval = text[clr_idx : cls_idx - 1].split(":")[1]
            vehicle_clr = " ".join(re.findall("[a-zA-Z]+", clrval))

        else:
            vehicle_clr = None

        if cls_idx != -1:
            clsval = text[cls_idx : type_idx - 1].split(":")[1]
            vehicle_clss = " ".join(re.findall("[a-zA-Z]+", clsval))

        else:
            vehicle_clss = None

        if type_idx != -1:
            typeval = text[type_idx : empt_idx - 1].split(":")[1]
            vehicle_type = " ".join(re.findall("[a-zA-Z]+", typeval))
            output = []
            for word in vehicle_type.split():
                if word not in output:
                    output.append(word)
                    vehicle_type = " ".join(output)

        else:
            vehicle_type = None

        if empt_idx != -1:
            emptval = text[empt_idx : grs_idx - 1].split(":")
            empty_weight = emptval[1]

        else:
            empty_weight = None

        if grs_idx != -1:
            grsval = text[grs_idx : engine_idx - 1].split(":")
            gross_weight = grsval[1]

        else:
            gross_weight = None

        if engine_idx != -1:
            engineval = text[engine_idx : chasis_idx - 1].split(":")
            engine_no = engineval[1]

        else:
            engine_no = None

        if chasis_idx != -1:
            chasisval = text[chasis_idx : rmrks_idx - 1].split(":")
            chasis_no = chasisval[1]

        else:
            chasis_no = None

    params = {
        "traffic_plate": traffic_plate,
        "place_of_issue": place_of_issue,
        "plate_cls": plate_cls,
        "traffic_code": traffic_code,
        "owner": owner,
        "ins_expiry": ins_expiry,
        "nationality": nationality,
        "policy_no": policy_no,
        "reg_date": reg_date,
        "ins_type": ins_type,
        "expiry_date": expiry_date,
        "passenger_no": passenger_no,
        "year_model": year_model,
        "origin": origin,
        "vehicle_clr": vehicle_clr,
        "vehicle_clss": vehicle_clss,
        "vehicle_type": vehicle_type,
        "empty_weight": empty_weight,
        "gross_weight": gross_weight,
        "engine_no": engine_no,
        "chasis_no": chasis_no,
    }

    return params


def rtaScannedData(filename1):
    # convert to jpg file after uploading
    img_file = pdf2image.convert_from_path(filename1, 500, poppler_path=poppler_path)
    image_counter1 = 1
    img_name = "test"

    for page in img_file:
        filename1 = img_name + str(image_counter1) + ".jpg"
        page.save(filename1, "JPEG")
        image_data = filename1
        reader = easyocr.Reader(["en", "ar"])
        img_text = reader.readtext(image_data)
        final_text = ""
        for _, text, __ in img_text:
            final_text += " "
            final_text += text
        text = final_text

        tp_idx = text.find("Traffic Plaie No")
        poi_idx = text.find("Plate of Issue")
        tc_idx = text.find("No,")
        owner_idx = text.find("Owner")
        natl_idx = text.find("Nationality")
        reg_idx = text.find("Date")
        ins_idx = text.find("Ins")

        policy_idx = text.find("Policy No")
        mortage_idx = text.find("Mortgage By")
        model_idx = text.find("Model")
        pax_idx = text.find("Num of Pass")
        orgin_idx = text.find("Origin")
        type_idx = text.find("Veh,")
        empt_idx = text.find("Empty Weight")
        chasis_idx = text.find("Chassis No")

        if tp_idx != -1:
            tpval = text[tp_idx : poi_idx - 1].split("Traffic Plaie No ")[1]
            traffic_plate = tpval[0:7]

        else:
            traffic_plate = None

        if poi_idx != -1:
            poival = text[poi_idx : tc_idx - 1].split("Plate of Issue")[1]
            place_of_issue = poival

        else:
            place_of_issue = None

        if tc_idx != -1:
            tcval = text[tc_idx : owner_idx - 1].split("No,")[1]
            # traffic_code = tcval#[1]
            traffic_code = " ".join(re.findall(r"\d[0-9\-]*", tcval))

        else:
            traffic_code = None

        if owner_idx != -1:
            onrval = text[owner_idx : natl_idx - 1].split("Owner")[1]
            owner = onrval  # " ".join(re.findall("[a-zA-Z]+", onrval))

        else:
            owner = None

        if natl_idx != -1:
            natlval = text[natl_idx : reg_idx - 1].split("Nationality")[1]
            nationality = " ".join(re.findall("[a-zA-Z]+", natlval))

        else:
            nationality = None

        if reg_idx != -1:
            regval = text[reg_idx : ins_idx - 1].split("Date")
            reg_date = " ".join(re.findall(r"\d[0-9\\]*", regval[2])).replace(" ", "/")[
                0:10
            ]
            expiry_date = " ".join(re.findall(r"\d[0-9\\]*", regval[1])).replace(
                " ", "/"
            )[0:10]

        else:
            reg_date = None
            expiry_date = None

        if ins_idx != -1:
            insval = text[ins_idx : policy_idx - 1]
            ins_expiry = " ".join(re.findall(r"\d[0-9\\]*", insval)).replace(" ", "/")[
                0:10
            ]

        else:
            ins_expiry = None

        if policy_idx != -1:
            polval = text[policy_idx : mortage_idx - 1]
            policy_no = " ".join(re.findall(r"\d[0-9\\]*", polval))

        else:
            policy_no = None

        if model_idx != -1:
            modelval = text[model_idx : pax_idx - 1].split("Model")
            year_model = modelval[1]

        else:
            year_model = None

        if pax_idx != -1:
            paxval = text[pax_idx : orgin_idx - 1]
            passenger_no = " ".join(re.findall(r"\d[0-9\\]*", paxval))

        else:
            passenger_no = None

        if orgin_idx != -1:
            orgval = text[orgin_idx : type_idx - 1].split("Origin")[1]
            origin = " ".join(re.findall("[a-zA-Z]+", orgval))

        else:
            origin = None

        if type_idx != -1:
            typeval = text[type_idx : empt_idx - 1].split("Veh,")[1]
            vehicle_type = " ".join(re.findall("[a-zA-Z]+", typeval))
            output = []
            for word in vehicle_type.split():
                if word not in output:
                    output.append(word)
                    vehicle_type = " ".join(output)
            gross_weight = " ".join(re.findall(r"\d+", typeval)).split(" ")[3]

        else:
            vehicle_type = None
            gross_weight = None

        if empt_idx != -1:
            emptval = text[empt_idx : chasis_idx - 1].split("Empty Weight")
            empt_wgt = emptval[1].split("No")[0]
            empty_weight = " ".join(re.findall(r"\d[0-9\\]*", empt_wgt))
            engine = emptval[1].split("No")[1].split(" ")
            engine = " ".join((engine[0:3]))
            engine_no = engine

        else:
            empty_weight = None
            engine_no = None

        if chasis_idx != -1:
            chasisval = text[chasis_idx:].split("Chassis No")
            chasis_no = chasisval[1].split(" ")[1]
        else:
            chasis_no = None
    if os.path.exists(filename1):
        os.remove(filename1)
    else:
        print("Can not delete the file as it doesn't exists")
    # os.remove(filename1 )
    params = {
        "traffic_plate": traffic_plate,
        "place_of_issue": place_of_issue,
        "plate_cls": "",
        "traffic_code": traffic_code,
        "owner": owner,
        "ins_expiry": ins_expiry,
        "nationality": nationality,
        "policy_no": policy_no,
        "reg_date": reg_date,
        "ins_type": "",
        "expiry_date": expiry_date,
        "passenger_no": passenger_no,
        "year_model": year_model,
        "origin": origin,
        "vehicle_clr": "",
        "vehicle_clss": "",
        "vehicle_type": vehicle_type,
        "empty_weight": empty_weight,
        "gross_weight": gross_weight,
        "engine_no": engine_no,
        "chasis_no": chasis_no,
    }

    return params
