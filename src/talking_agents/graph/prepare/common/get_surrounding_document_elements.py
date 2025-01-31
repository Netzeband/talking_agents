from typeguard import typechecked
from unstructured.documents.elements import Element, NarrativeText

from .no_text_element_categories import NO_TEXT_ELEMENT_CATEGORIES


@typechecked()
def get_surrounding_document_elements(
        document: list[Element],
        index: int,
        text_length: int,
) -> tuple[list[Element], Element, list[Element]]:
    element = document[index]
    elements_before = _limit_reverse_section_text(
        [e for e in document[:index] if e.category not in NO_TEXT_ELEMENT_CATEGORIES],
        text_length
    )
    elements_after = _limit_section_text(
        [e for e in document[index:] if e.category not in NO_TEXT_ELEMENT_CATEGORIES],
        text_length
    )

    return elements_before, element, elements_after


@typechecked()
def _limit_section_text(elements: list[Element], text_length: int) -> list[Element]:
    text = ""
    output_elements = []
    for element in elements:
        if len(text) + len(element.text) <= text_length:
            text += element.text
            output_elements.append(element)

        else:
            remaining_length = text_length - len(text)
            remaining_section_text = element.text[:remaining_length] + "..."
            output_elements.append(NarrativeText(
                text=remaining_section_text,
                element_id=element.id,
                metadata=element.metadata,
            ))
            break

    return output_elements


@typechecked()
def _limit_reverse_section_text(elements: list[Element], text_length: int) -> list[Element]:
    text = ""
    output_elements: list[Element] = []
    for element in reversed(elements):
        if len(text) + len(element.text) <= text_length:
            text += element.text
            output_elements.append(element)

        else:
            remaining_length = text_length - len(text)
            remaining_section_text = "..." + element.text[-remaining_length:]
            output_elements.append(NarrativeText(
                text=remaining_section_text,
                element_id=element.id,
                metadata=element.metadata,
            ))
            break

    return list(reversed(output_elements))
