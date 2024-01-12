from re import fullmatch

from .physdesc_to_extent import PhysdescToExtent


def get_dates(self):
    as_client = PhysdescToExtent("dev").as_client
    for resource in as_client.aspace.repositories(2).resources:
        if resource.publish and not resource.suppressed:
            for date in resource.dates:
                expression = date.json().get("expression")
                begin = date.json().get("begin")
                end = date.json().get("end")
                date_type = date.json().get("date_type")

def normalize_expression(self, expression):
    if fullmatch(r"\d\d\d\d-\d\d\d\d", expression) and begin == "None" and end == "None":
        begin = expression.split("-")[0]
        end = expression.split("-")[-1]
        date_type = "inclusive"
    else: 
        pass
