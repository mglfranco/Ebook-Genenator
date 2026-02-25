"""Modelos Pydantic para a API Geradora de E-books V3."""

from typing import Optional

from pydantic import BaseModel, Field, model_validator


# ---------------------------------------------------------------------------
# Modelo para o endpoint /generate-ebook (conteúdo fornecido)
# ---------------------------------------------------------------------------
class Chapter(BaseModel):
    """Um capítulo com título e conteúdo em Markdown."""
    title: str = Field(..., description="Título do capítulo", min_length=1)
    content: str = Field(..., description="Corpo do capítulo em Markdown", min_length=1)


class EbookRequest(BaseModel):
    """Payload para /generate-ebook (conteúdo já escrito)."""
    title: str = Field(..., description="Título do livro", min_length=1)
    author: str = Field(..., description="Nome do autor", min_length=1)
    chapter_count: Optional[int] = Field(
        default=None,
        description="Quantidade de capítulos (calculado automaticamente se omitido)",
        ge=1,
    )
    theme: str = Field(
        default="Minimalista Moderno",
        description="Tema visual da obra",
    )
    chapters: list[Chapter] = Field(
        ..., description="Lista de capítulos com conteúdo", min_length=1
    )

    @model_validator(mode="after")
    def validar_contagem(self):
        if self.chapter_count is None:
            self.chapter_count = len(self.chapters)
        elif len(self.chapters) != self.chapter_count:
            raise ValueError(
                f"chapter_count ({self.chapter_count}) ≠ chapters ({len(self.chapters)})"
            )
        return self


# ---------------------------------------------------------------------------
# Modelo para o endpoint /generate-from-form (conteúdo gerado pelo Gemini)
# ---------------------------------------------------------------------------
class FormChapter(BaseModel):
    """Capítulo do formulário: apenas título + quantidade de páginas."""
    title: str = Field(..., description="Título do capítulo", min_length=1)
    pages: int = Field(default=5, description="Quantidade de páginas para este capítulo", ge=1, le=30)


class EbookFormRequest(BaseModel):
    """Payload do formulário web (conteúdo gerado automaticamente)."""
    title: str = Field(..., description="Título do livro", min_length=1)
    author: str = Field(default="Autor", description="Nome do autor", min_length=1)
    chapter_count: Optional[int] = Field(default=None, ge=1)
    theme: str = Field(
        default="Minimalista Moderno",
        description="Tema visual e direcional da obra",
    )
    chapters: list[FormChapter] = Field(
        ..., description="Lista de capítulos (título + páginas)", min_length=1
    )

    @model_validator(mode="after")
    def validar_contagem(self):
        if self.chapter_count is None:
            self.chapter_count = len(self.chapters)
        return self
