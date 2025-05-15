from pydantic import BaseModel

class Taxpayer(BaseModel):
    """
    Taxpayer class for data validation with Pydantic
    """
    name: str = ""
    firstnames: str = ""
    activity: list[str] = []
    address: list[str] = []
    title:list[str] = []
    familystatus:list[str] = []
    birthname: str = ""

class TaxpayersList(BaseModel):
    """
    TaxpayersList class for data validation with Pydantic
    """
    taxpayers: list[Taxpayer]

def create_brat_entity_T(index:int, text:str,start:int,end:int,ent_type:str):
    """
    Args:
        index:    int, used to build the unique identifier of an entity (from one input)
        text:     str, text of the entity
        start:    int, index of the first character of the entity in the input
        end:      int, index of the last+1 character of the entity in the input
        ent_type: str, type of named entity
        
    Returns:
        A string describing a named entity (T), structured as required in a .ann file of the brat format
    """
    line = "T" + str(index) + '\t' + text + ' ' + str(start) + ' ' + str(end) +  '\t' + ent_type + '\n'
    print(line)
    return line