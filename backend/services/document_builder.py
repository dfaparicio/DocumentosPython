"""
Constructor de documentos usando el algoritmo Try-Face-First.
Agrupa páginas de un PDF en documentos lógicos basándose en el tipo de cara.
"""

from typing import Dict, List, Optional, Tuple
from services.face_classifier import get_classifier, FaceClassifier
from services.mixed_face_detector import get_detector
from services.image_splitter import split_image_by_coordinates


class Document:
    """
    Representa un documento con una o dos caras.
    """

    def __init__(self, document_type: str):
        """
        Inicializa un documento.

        Args:
            document_type: Tipo de documento (ej: "cedula_ciudadania_vieja")
        """
        self.document_type = document_type
        self.front_face: Optional[bytes] = None
        self.back_face: Optional[bytes] = None
        self.is_complete: bool = False
        self.is_one_face: bool = False
        self.page_number: int = -1  # Número de página donde se encontró

    def add_front_face(self, image: bytes, page_number: int = 0):
        """
        Agrega la cara frontal del documento.

        Args:
            image: Imagen de la cara frontal
            page_number: Número de página donde se encontró
        """
        self.front_face = image
        if self.page_number == -1:
            self.page_number = page_number

    def add_back_face(self, image: bytes):
        """
        Agrega la cara trasera del documento.

        Args:
            image: Imagen de la cara trasera
        """
        self.back_face = image

    def mark_complete(self):
        """Marca el documento como completo."""
        self.is_complete = True

    def mark_one_face(self):
        """Marca el documento como de una sola cara."""
        self.is_one_face = True

    def has_front_face(self) -> bool:
        """Retorna True si tiene cara frontal."""
        return self.front_face is not None

    def has_back_face(self) -> bool:
        """Retorna True si tiene cara trasera."""
        return self.back_face is not None

    def to_dict(self) -> Dict[str, any]:
        """
        Convierte el documento a un diccionario.

        Returns:
            Diccionario con la información del documento
        """
        return {
            "document_type": self.document_type,
            "front_face": self.front_face,
            "back_face": self.back_face,
            "is_complete": self.is_complete,
            "is_one_face": self.is_one_face,
            "page_number": self.page_number
        }


class DocumentBuilder:
    """
    Constructor de documentos usando el algoritmo Try-Face-First.

    Algoritmo:
    1. Para cada página del PDF, clasificar el tipo de cara
    2. Si es FRONTAL, crear nuevo documento
    3. Si es TRASERA, agregar al documento anterior (si existe y no tiene trasera)
    4. Si es COMPLETO, crear documento de 1 cara y marcar como completo
    5. Si es MIXTO, dividir y procesar como dos caras
    """

    def __init__(self, classifier: Optional[FaceClassifier] = None):
        """
        Inicializa el constructor de documentos.

        Args:
            classifier: Instancia del clasificador de caras (opcional, se crea uno si no se proporciona)
        """
        self.classifier = classifier or get_classifier()
        self.detector = get_detector()
        self.current_document: Optional[Document] = None
        self.documents: List[Document] = []

    def process_pdf_pages(self, pages: List[bytes]) -> List[Document]:
        """
        Procesa una lista de páginas del PDF y construye documentos.

        Args:
            pages: Lista de imágenes de páginas en bytes

        Returns:
            Lista de documentos construidos
        """
        self.documents = []
        self.current_document = None

        for page_index, page in enumerate(pages):
            self._process_page(page, page_index)

        # Si quedó un documento incompleto al final, lo marcamos como de 1 cara
        if self.current_document and not self.current_document.is_complete:
            self.current_document.mark_one_face()
            self.documents.append(self.current_document)
            self.current_document = None

        return self.documents

    def _process_page(self, page: bytes, page_number: int = 0):
        """
        Procesa una sola página del PDF.

        Args:
            page: Imagen de la página en bytes
            page_number: Número de página
        """
        # Primero, clasificamos la página
        classification = self.classifier.classify(page)
        face_type = classification.get("face_type", "DESCONOCIDO")
        document_type = classification.get("document_type", "otro")

        # Manejamos según el tipo de cara
        if face_type == "MIXTO":
            self._handle_mixed_face(page, page_number, document_type)
        elif face_type == "COMPLETO":
            self._handle_complete_face(page, page_number, document_type)
        elif face_type == "FRONTAL":
            self._handle_frontal_face(page, page_number, document_type)
        elif face_type == "TRASERA":
            self._handle_trasera_face(page, page_number, document_type)
        else:
            # DESCONOCIDO: tratamos como documento de 1 cara
            self._handle_unknown_face(page, page_number, document_type)

    def _handle_mixed_face(self, page: bytes, page_number: int, document_type: str):
        """
        Maneja una página que contiene dos caras (mixta).

        Args:
            page: Imagen de la página en bytes
            page_number: Número de página
            document_type: Tipo de documento detectado
        """
        # Intentamos dividir la página mixta
        split_result = self.detector.split_mixed_page(page)

        if split_result:
            cara1, cara2 = split_result

            # Clasificamos cada cara individualmente
            classification1 = self.classifier.classify(cara1)
            classification2 = self.classifier.classify(cara2)

            # Procesamos la primera cara
            if classification1.get("face_type") == "FRONTAL":
                self._handle_frontal_face(cara1, page_number, document_type)
            elif classification1.get("face_type") == "TRASERA":
                self._handle_trasera_face(cara1, page_number, document_type)

            # Procesamos la segunda cara
            if classification2.get("face_type") == "TRASERA":
                self._handle_trasera_face(cara2, page_number, document_type)
            elif classification2.get("face_type") == "FRONTAL":
                # Si la segunda cara es frontal, iniciamos un nuevo documento
                # Esto puede pasar si la división no fue perfecta
                self._handle_frontal_face(cara2, page_number, document_type)

            # Si después de procesar ambas caras el documento está completo, lo guardamos
            if self.current_document and self.current_document.is_complete:
                self.documents.append(self.current_document)
                self.current_document = None
        else:
            # Si no podemos dividir, tratamos como una sola cara
            print(f"No se pudo dividir la página mixta en la página {page_number}")
            self._handle_unknown_face(page, page_number, document_type)

    def _handle_complete_face(self, page: bytes, page_number: int, document_type: str):
        """
        Maneja una página que es un documento completo de 1 cara (ej: pasaporte).

        Args:
            page: Imagen de la página en bytes
            page_number: Número de página
            document_type: Tipo de documento detectado
        """
        # Primero, guardamos el documento actual si existe y está completo
        if self.current_document and self.current_document.is_complete:
            self.documents.append(self.current_document)
            self.current_document = None

        # Creamos un nuevo documento de 1 cara
        doc = Document(document_type)
        doc.add_front_face(page, page_number)
        doc.mark_one_face()
        doc.mark_complete()

        self.documents.append(doc)

    def _handle_frontal_face(self, page: bytes, page_number: int, document_type: str):
        """
        Maneja una página que es una cara frontal.

        Args:
            page: Imagen de la página en bytes
            page_number: Número de página
            document_type: Tipo de documento detectado
        """
        # Si hay un documento actual incompleto, lo guardamos
        # Esto puede pasar si teníamos una frontal sin su trasera
        if self.current_document and not self.current_document.is_complete:
            self.current_document.mark_one_face()
            self.documents.append(self.current_document)

        # Si hay un documento actual completo, lo guardamos
        if self.current_document and self.current_document.is_complete:
            self.documents.append(self.current_document)

        # Creamos un nuevo documento con esta cara frontal
        self.current_document = Document(document_type)
        self.current_document.add_front_face(page, page_number)

    def _handle_trasera_face(self, page: bytes, page_number: int, document_type: str):
        """
        Maneja una página que es una cara trasera.

        Args:
            page: Imagen de la página en bytes
            page_number: Número de página
            document_type: Tipo de documento detectado
        """
        # Intentamos agregar al documento actual
        if (self.current_document and
            not self.current_document.has_back_face() and
            self.current_document.document_type == document_type):
            # El documento actual no tiene cara trasera y es del mismo tipo
            self.current_document.add_back_face(page)
            self.current_document.mark_complete()
        else:
            # No hay documento activo, ya tiene trasera, o es de diferente tipo
            # Creamos un documento de 1 cara
            doc = Document(document_type)
            doc.add_front_face(page, page_number)
            doc.mark_one_face()
            doc.mark_complete()
            self.documents.append(doc)

    def _handle_unknown_face(self, page: bytes, page_number: int, document_type: str):
        """
        Maneja una página de tipo desconocido.

        Args:
            page: Imagen de la página en bytes
            page_number: Número de página
            document_type: Tipo de documento detectado (o "otro")
        """
        # Creamos un documento de 1 cara
        doc = Document(document_type)
        doc.add_front_face(page, page_number)
        doc.mark_one_face()
        doc.mark_complete()
        self.documents.append(doc)

    def get_documents(self) -> List[Document]:
        """
        Retorna la lista de documentos construidos.

        Returns:
            Lista de documentos
        """
        return self.documents

    def clear(self):
        """Limpia el estado del constructor."""
        self.current_document = None
        self.documents = []

    def get_statistics(self) -> Dict[str, any]:
        """
        Retorna estadísticas de los documentos construidos.

        Returns:
            Diccionario con estadísticas
        """
        total = len(self.documents)
        one_face = sum(1 for d in self.documents if d.is_one_face)
        two_face = total - one_face

        # Contar por tipo de documento
        by_type = {}
        for doc in self.documents:
            doc_type = doc.document_type
            by_type[doc_type] = by_type.get(doc_type, 0) + 1

        return {
            "total_documents": total,
            "one_face_documents": one_face,
            "two_face_documents": two_face,
            "by_type": by_type
        }


def build_documents_from_pages(pages: List[bytes]) -> List[Dict[str, any]]:
    """
    Función de conveniencia para construir documentos desde una lista de páginas.

    Args:
        pages: Lista de imágenes de páginas en bytes

    Returns:
        Lista de diccionarios con la información de los documentos
    """
    builder = DocumentBuilder()
    documents = builder.process_pdf_pages(pages)

    # Convertimos a diccionarios
    return [doc.to_dict() for doc in documents]
