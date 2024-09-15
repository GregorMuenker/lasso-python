# Generated from LQL.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .LQLParser import LQLParser
else:
    from LQLParser import LQLParser

# This class defines a complete generic visitor for a parse tree produced by LQLParser.

class LQLVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by LQLParser#parse.
    def visitParse(self, ctx:LQLParser.ParseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LQLParser#interfaceSpec.
    def visitInterfaceSpec(self, ctx:LQLParser.InterfaceSpecContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LQLParser#methodSig.
    def visitMethodSig(self, ctx:LQLParser.MethodSigContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LQLParser#parameters.
    def visitParameters(self, ctx:LQLParser.ParametersContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LQLParser#inputs.
    def visitInputs(self, ctx:LQLParser.InputsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LQLParser#outputs.
    def visitOutputs(self, ctx:LQLParser.OutputsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LQLParser#qualifiedtype.
    def visitQualifiedtype(self, ctx:LQLParser.QualifiedtypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LQLParser#simpletype.
    def visitSimpletype(self, ctx:LQLParser.SimpletypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LQLParser#arraytype.
    def visitArraytype(self, ctx:LQLParser.ArraytypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LQLParser#namedparam.
    def visitNamedparam(self, ctx:LQLParser.NamedparamContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LQLParser#typeparam.
    def visitTypeparam(self, ctx:LQLParser.TypeparamContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LQLParser#filter.
    def visitFilter(self, ctx:LQLParser.FilterContext):
        return self.visitChildren(ctx)



del LQLParser