from abc import ABC, abstractmethod

from partituras.modelo.errores import (
    ContieneNumero,
    ContieneCaracterInvalido,
    SinNotas,
    EspacioMultiple,
    EspacioBordes,
)

NOTAS = ["do", "re", "mi", "fa", "sol", "la", "si"]

FRECUENCIAS = {
    "do": 261,
    "re": 293,
    "mi": 329,
    "fa": 349,
    "sol": 392,
    "la": 440,
    "si": 493,
}

class ReglaTransformacion(ABC):

    def __init__(self, token: int):
        self.token = token

    @abstractmethod
    def transformar(self, partitura: str) -> str:
        pass

    @abstractmethod
    def revertir(self, partitura: str) -> str:
        pass

    @abstractmethod
    def partitura_valida(self, partitura: str) -> bool:
        pass

    def encontrar_numeros_partitura(self, partitura: str) -> list:
        return [
            (i, caracter)
            for i, caracter in enumerate(partitura)
            if caracter.isdigit()
        ]

    def encontrar_caracteres_invalidos(self, partitura: str) -> list:
        return [
            (i, caracter)
            for i, caracter in enumerate(partitura)
            if ord(caracter) > 127
        ]

class ReglaTransformacion(ABC):

    def __init__(self, token: int):
        self.token = token

    @abstractmethod
    def transformar(self, partitura: str) -> str:
        pass

    @abstractmethod
    def revertir(self, partitura: str) -> str:
        pass

    @abstractmethod
    def partitura_valida(self, partitura: str) -> bool:
        pass

    def encontrar_numeros_partitura(self, partitura: str) -> list:
        return [
            (i, caracter)
            for i, caracter in enumerate(partitura)
            if caracter.isdigit()
        ]

    def encontrar_caracteres_invalidos(self, partitura: str) -> list:
        return [
            (i, caracter)
            for i, caracter in enumerate(partitura)
            if ord(caracter) > 127
        ]

class ReglaTransposicion(ReglaTransformacion):

    def partitura_valida(self, partitura: str) -> bool:

        errores = []

        numeros = self.encontrar_numeros_partitura(partitura)

        if numeros:
            mensaje = ", ".join(
                [f"posición {i}: '{c}'" for i, c in numeros]
            )
            errores.append(
                ContieneNumero(
                    f"La partitura contiene números -> {mensaje}"
                )
            )

        invalidos_ascii = self.encontrar_caracteres_invalidos(partitura)

        if invalidos_ascii:
            mensaje = ", ".join(
                [f"posición {i}: '{c}'" for i, c in invalidos_ascii]
            )
            errores.append(
                ContieneCaracterInvalido(
                    f"Caracteres no ASCII -> {mensaje}"
                )
            )

        partitura = partitura.lower()

        tokens = partitura.split()

        permitidos = set(NOTAS + ["|", "-"])

        invalidos = [
            (i, token)
            for i, token in enumerate(tokens)
            if token not in permitidos
        ]

        if invalidos:
            mensaje = ", ".join(
                [f"token {i}: '{t}'" for i, t in invalidos]
            )
            errores.append(
                ContieneCaracterInvalido(
                    f"Tokens inválidos -> {mensaje}"
                )
            )

        notas = [t for t in tokens if t in NOTAS]

        if not notas:
            errores.append(
                SinNotas(
                    "La partitura debe contener al menos una nota"
                )
            )

        if errores:
            raise ExceptionGroup(
                "Errores de validación",
                errores
            )

        return True

    def transformar(self, partitura: str) -> str:

        self.partitura_valida(partitura)

        partitura = partitura.lower()

        resultado = []

        for token in partitura.split():

            if token in ["|", "-"]:
                resultado.append(token)
            else:
                indice = NOTAS.index(token)
                nuevo = NOTAS[(indice + self.token) % len(NOTAS)]
                resultado.append(nuevo)

        return " ".join(resultado)

    def revertir(self, partitura: str) -> str:

        self.partitura_valida(partitura)

        partitura = partitura.lower()

        resultado = []

        for token in partitura.split():

            if token in ["|", "-"]:
                resultado.append(token)
            else:
                indice = NOTAS.index(token)
                nuevo = NOTAS[(indice - self.token) % len(NOTAS)]
                resultado.append(nuevo)

        return " ".join(resultado)

class ReglaFrecuencia(ReglaTransformacion):

    def partitura_valida(self, partitura: str) -> bool:

        errores = []

        numeros = self.encontrar_numeros_partitura(partitura)

        if numeros:
            mensaje = ", ".join(
                [f"posición {i}: '{c}'" for i, c in numeros]
            )
            errores.append(
                ContieneNumero(
                    f"La partitura contiene números -> {mensaje}"
                )
            )

        invalidos_ascii = self.encontrar_caracteres_invalidos(partitura)

        if invalidos_ascii:
            mensaje = ", ".join(
                [f"posición {i}: '{c}'" for i, c in invalidos_ascii]
            )
            errores.append(
                ContieneCaracterInvalido(
                    f"Caracteres no ASCII -> {mensaje}"
                )
            )

        if partitura != partitura.strip():
            errores.append(
                EspacioBordes(
                    "La partitura no puede tener espacios al inicio o final"
                )
            )

        if "  " in partitura:
            errores.append(
                EspacioMultiple(
                    "La partitura no puede tener múltiples espacios consecutivos"
                )
            )

        partitura = partitura.lower()

        tokens = partitura.split(" ")

        invalidos = [
            (i, token)
            for i, token in enumerate(tokens)
            if token not in NOTAS
        ]

        if invalidos:
            mensaje = ", ".join(
                [f"token {i}: '{t}'" for i, t in invalidos]
            )
            errores.append(
                ContieneCaracterInvalido(
                    f"Notas inválidas -> {mensaje}"
                )
            )

        if errores:
            raise ExceptionGroup(
                "Errores de validación",
                errores
            )

        return True

    def transformar(self, partitura: str) -> str:

        self.partitura_valida(partitura)

        partitura = partitura.lower()

        return " ".join(
            [
                str(FRECUENCIAS[nota] * self.token)
                for nota in partitura.split(" ")
            ]
        )

    def revertir(self, partitura: str) -> str:

        valores = [float(x) for x in partitura.split()]

        resultado = []

        for valor in valores:

            frecuencia = valor / self.token

            nota = next(
                nota
                for nota, freq in FRECUENCIAS.items()
                if freq == frecuencia
            )

            resultado.append(nota)

        return " ".join(resultado)