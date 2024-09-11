"""
Instructions:
curl -O https://www.antlr.org/download/antlr-4.13.2-complete.jar
pip3 install antlr4-python3-runtime
java -jar antlr-4.13.2-complete.jar LQL.g4 -Dlanguage=Python3
java -jar antlr-4.13.2-complete.jar -Dlanguage=Python3 -visitor LQL.g4
"""

import sys
import git
repo = git.Repo(search_parent_directories=True)
sys.path.insert(0, repo.working_tree_dir)

sys.path.insert(1, "../lql")
sys.path.insert(1, "../arena")
sys.path.insert(1, "../../backend")

from antlr4 import *
from LQLLexer import LQLLexer
from LQLParser import LQLParser
from LQLVisitor import LQLVisitor
from backend.arena.adaptation_identification import MethodSignature, InterfaceSpecification
from backend.constants import RED, RESET


class LQLCustomVisitor(LQLVisitor):
    def __init__(self):
        super().__init__()
        self.interfaceSpecification = None

    def visitParse(self, ctx: LQLParser.ParseContext):
        result = None
        if ctx.interfaceSpec():
            result = self.visit(ctx.interfaceSpec())
        return result

    def visitInterfaceSpec(self, ctx: LQLParser.InterfaceSpecContext):
        className = ctx.NAME().getText()
        constructors = []
        methods = []

        for methodCtx in ctx.methodSig():
            method = self.visitMethodSig(methodCtx)
            if method.methodName == className:
                constructors.append(method)
            else:
                methods.append(method)

        if len(constructors) > 1:
            print(
                f"{RED}Warning:{RESET} LASSO Python does not support more than one constructor, only the first one will be considered."
            )
        constructor = constructors[0] if constructors else None

        self.interfaceSpecification = InterfaceSpecification(
            className, constructor, methods
        )
        print("Interface Specification:", self.interfaceSpecification)  # Debugging
        return self.interfaceSpecification

    def visitMethodSig(self, ctx: LQLParser.MethodSigContext):
        methodName = ctx.NAME().getText()
        parameterTypes = self.visit(ctx.inputs()) if ctx.inputs() else []
        returnType = self.visit(ctx.outputs()) if ctx.outputs() else None
        return MethodSignature(methodName, returnType, parameterTypes)

    def visitInputs(self, ctx: LQLParser.InputsContext):
        return self.visit(ctx.parameters())

    def visitOutputs(self, ctx: LQLParser.OutputsContext):
        parameters = self.visit(ctx.parameters())
        return parameters[0] if parameters else None

    def visitParameters(self, ctx: LQLParser.ParametersContext):
        parameterTypes = []
        for paramCtx in ctx.getChildren():
            if isinstance(paramCtx, LQLParser.SimpletypeContext) or isinstance(
                paramCtx, LQLParser.QualifiedtypeContext
            ):
                parameterTypes.append(paramCtx.getText())
            elif isinstance(paramCtx, LQLParser.ArraytypeContext):
                parameterTypes.append(paramCtx.getText())
            elif isinstance(paramCtx, LQLParser.NamedparamContext):
                parameterTypes.append(paramCtx.getText().split("=")[1])
            elif isinstance(paramCtx, LQLParser.TypeparamContext):
                parameterTypes.append(paramCtx.getText())
        return parameterTypes


def parse_interface_spec(input_text):
    input_stream = InputStream(input_text)
    lexer = LQLLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = LQLParser(stream)
    tree = parser.parse()

    visitor = LQLCustomVisitor()
    interface_specification = visitor.visit(tree)
    return interface_specification


if __name__ == "__main__":
    # Example input string
    input_text = """
    Calculator {
        Calculator(int)
        Calculator(str)
        log(int, int)->float
        sqrd(int)->int
    }
    """

    # Parse the input
    interface_spec = parse_interface_spec(input_text)
