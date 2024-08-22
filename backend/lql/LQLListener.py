# Generated from LQL.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .LQLParser import LQLParser
else:
    from LQLParser import LQLParser

# This class defines a complete listener for a parse tree produced by LQLParser.
class LQLListener(ParseTreeListener):

    # Enter a parse tree produced by LQLParser#parse.
    def enterParse(self, ctx:LQLParser.ParseContext):
        pass

    # Exit a parse tree produced by LQLParser#parse.
    def exitParse(self, ctx:LQLParser.ParseContext):
        pass


    # Enter a parse tree produced by LQLParser#interfaceSpec.
    def enterInterfaceSpec(self, ctx:LQLParser.InterfaceSpecContext):
        pass

    # Exit a parse tree produced by LQLParser#interfaceSpec.
    def exitInterfaceSpec(self, ctx:LQLParser.InterfaceSpecContext):
        pass


    # Enter a parse tree produced by LQLParser#methodSig.
    def enterMethodSig(self, ctx:LQLParser.MethodSigContext):
        pass

    # Exit a parse tree produced by LQLParser#methodSig.
    def exitMethodSig(self, ctx:LQLParser.MethodSigContext):
        pass


    # Enter a parse tree produced by LQLParser#parameters.
    def enterParameters(self, ctx:LQLParser.ParametersContext):
        pass

    # Exit a parse tree produced by LQLParser#parameters.
    def exitParameters(self, ctx:LQLParser.ParametersContext):
        pass


    # Enter a parse tree produced by LQLParser#inputs.
    def enterInputs(self, ctx:LQLParser.InputsContext):
        pass

    # Exit a parse tree produced by LQLParser#inputs.
    def exitInputs(self, ctx:LQLParser.InputsContext):
        pass


    # Enter a parse tree produced by LQLParser#outputs.
    def enterOutputs(self, ctx:LQLParser.OutputsContext):
        pass

    # Exit a parse tree produced by LQLParser#outputs.
    def exitOutputs(self, ctx:LQLParser.OutputsContext):
        pass


    # Enter a parse tree produced by LQLParser#qualifiedtype.
    def enterQualifiedtype(self, ctx:LQLParser.QualifiedtypeContext):
        pass

    # Exit a parse tree produced by LQLParser#qualifiedtype.
    def exitQualifiedtype(self, ctx:LQLParser.QualifiedtypeContext):
        pass


    # Enter a parse tree produced by LQLParser#simpletype.
    def enterSimpletype(self, ctx:LQLParser.SimpletypeContext):
        pass

    # Exit a parse tree produced by LQLParser#simpletype.
    def exitSimpletype(self, ctx:LQLParser.SimpletypeContext):
        pass


    # Enter a parse tree produced by LQLParser#arraytype.
    def enterArraytype(self, ctx:LQLParser.ArraytypeContext):
        pass

    # Exit a parse tree produced by LQLParser#arraytype.
    def exitArraytype(self, ctx:LQLParser.ArraytypeContext):
        pass


    # Enter a parse tree produced by LQLParser#namedparam.
    def enterNamedparam(self, ctx:LQLParser.NamedparamContext):
        pass

    # Exit a parse tree produced by LQLParser#namedparam.
    def exitNamedparam(self, ctx:LQLParser.NamedparamContext):
        pass


    # Enter a parse tree produced by LQLParser#typeparam.
    def enterTypeparam(self, ctx:LQLParser.TypeparamContext):
        pass

    # Exit a parse tree produced by LQLParser#typeparam.
    def exitTypeparam(self, ctx:LQLParser.TypeparamContext):
        pass


    # Enter a parse tree produced by LQLParser#filter.
    def enterFilter(self, ctx:LQLParser.FilterContext):
        pass

    # Exit a parse tree produced by LQLParser#filter.
    def exitFilter(self, ctx:LQLParser.FilterContext):
        pass



del LQLParser