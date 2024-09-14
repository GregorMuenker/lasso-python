# Generated from LQL.g4 by ANTLR 4.13.2
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,15,138,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,1,0,3,0,26,8,0,1,0,
        5,0,29,8,0,10,0,12,0,32,9,0,1,0,1,0,1,1,1,1,1,1,5,1,39,8,1,10,1,
        12,1,42,9,1,1,1,1,1,1,2,1,2,1,2,3,2,49,8,2,1,2,1,2,3,2,53,8,2,1,
        2,1,2,3,2,57,8,2,1,2,3,2,60,8,2,1,3,1,3,1,3,1,3,1,3,3,3,67,8,3,1,
        3,1,3,1,3,1,3,1,3,1,3,3,3,75,8,3,5,3,77,8,3,10,3,12,3,80,9,3,1,4,
        1,4,1,5,1,5,1,6,1,6,1,6,5,6,89,8,6,10,6,12,6,92,9,6,1,7,1,7,1,8,
        1,8,3,8,98,8,8,1,8,5,8,101,8,8,10,8,12,8,104,9,8,1,9,1,9,1,9,1,9,
        1,9,3,9,111,8,9,1,10,1,10,3,10,115,8,10,1,10,1,10,1,10,1,10,3,10,
        121,8,10,1,10,1,10,1,10,1,10,3,10,127,8,10,5,10,129,8,10,10,10,12,
        10,132,9,10,1,10,1,10,1,11,1,11,1,11,0,0,12,0,2,4,6,8,10,12,14,16,
        18,20,22,0,0,152,0,25,1,0,0,0,2,35,1,0,0,0,4,45,1,0,0,0,6,66,1,0,
        0,0,8,81,1,0,0,0,10,83,1,0,0,0,12,85,1,0,0,0,14,93,1,0,0,0,16,97,
        1,0,0,0,18,105,1,0,0,0,20,114,1,0,0,0,22,135,1,0,0,0,24,26,3,2,1,
        0,25,24,1,0,0,0,25,26,1,0,0,0,26,30,1,0,0,0,27,29,3,22,11,0,28,27,
        1,0,0,0,29,32,1,0,0,0,30,28,1,0,0,0,30,31,1,0,0,0,31,33,1,0,0,0,
        32,30,1,0,0,0,33,34,5,0,0,1,34,1,1,0,0,0,35,36,5,12,0,0,36,40,5,
        1,0,0,37,39,3,4,2,0,38,37,1,0,0,0,39,42,1,0,0,0,40,38,1,0,0,0,40,
        41,1,0,0,0,41,43,1,0,0,0,42,40,1,0,0,0,43,44,5,2,0,0,44,3,1,0,0,
        0,45,59,5,12,0,0,46,48,5,3,0,0,47,49,3,8,4,0,48,47,1,0,0,0,48,49,
        1,0,0,0,49,50,1,0,0,0,50,52,5,4,0,0,51,53,3,10,5,0,52,51,1,0,0,0,
        52,53,1,0,0,0,53,60,1,0,0,0,54,56,5,3,0,0,55,57,3,8,4,0,56,55,1,
        0,0,0,56,57,1,0,0,0,57,58,1,0,0,0,58,60,5,5,0,0,59,46,1,0,0,0,59,
        54,1,0,0,0,60,5,1,0,0,0,61,67,3,14,7,0,62,67,3,12,6,0,63,67,3,16,
        8,0,64,67,3,18,9,0,65,67,3,20,10,0,66,61,1,0,0,0,66,62,1,0,0,0,66,
        63,1,0,0,0,66,64,1,0,0,0,66,65,1,0,0,0,67,78,1,0,0,0,68,74,5,6,0,
        0,69,75,3,14,7,0,70,75,3,12,6,0,71,75,3,16,8,0,72,75,3,18,9,0,73,
        75,3,20,10,0,74,69,1,0,0,0,74,70,1,0,0,0,74,71,1,0,0,0,74,72,1,0,
        0,0,74,73,1,0,0,0,75,77,1,0,0,0,76,68,1,0,0,0,77,80,1,0,0,0,78,76,
        1,0,0,0,78,79,1,0,0,0,79,7,1,0,0,0,80,78,1,0,0,0,81,82,3,6,3,0,82,
        9,1,0,0,0,83,84,3,6,3,0,84,11,1,0,0,0,85,90,5,12,0,0,86,87,5,7,0,
        0,87,89,5,12,0,0,88,86,1,0,0,0,89,92,1,0,0,0,90,88,1,0,0,0,90,91,
        1,0,0,0,91,13,1,0,0,0,92,90,1,0,0,0,93,94,5,12,0,0,94,15,1,0,0,0,
        95,98,3,14,7,0,96,98,3,12,6,0,97,95,1,0,0,0,97,96,1,0,0,0,98,102,
        1,0,0,0,99,101,5,8,0,0,100,99,1,0,0,0,101,104,1,0,0,0,102,100,1,
        0,0,0,102,103,1,0,0,0,103,17,1,0,0,0,104,102,1,0,0,0,105,106,5,12,
        0,0,106,110,5,9,0,0,107,111,3,14,7,0,108,111,3,12,6,0,109,111,3,
        16,8,0,110,107,1,0,0,0,110,108,1,0,0,0,110,109,1,0,0,0,111,19,1,
        0,0,0,112,115,3,14,7,0,113,115,3,12,6,0,114,112,1,0,0,0,114,113,
        1,0,0,0,115,116,1,0,0,0,116,120,5,10,0,0,117,121,3,14,7,0,118,121,
        3,12,6,0,119,121,3,20,10,0,120,117,1,0,0,0,120,118,1,0,0,0,120,119,
        1,0,0,0,121,130,1,0,0,0,122,126,5,6,0,0,123,127,3,14,7,0,124,127,
        3,12,6,0,125,127,3,20,10,0,126,123,1,0,0,0,126,124,1,0,0,0,126,125,
        1,0,0,0,127,129,1,0,0,0,128,122,1,0,0,0,129,132,1,0,0,0,130,128,
        1,0,0,0,130,131,1,0,0,0,131,133,1,0,0,0,132,130,1,0,0,0,133,134,
        5,11,0,0,134,21,1,0,0,0,135,136,5,13,0,0,136,23,1,0,0,0,18,25,30,
        40,48,52,56,59,66,74,78,90,97,102,110,114,120,126,130
    ]

class LQLParser ( Parser ):

    grammarFileName = "LQL.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'{'", "'}'", "'('", "')->'", "')'", "','", 
                     "'.'", "'[]'", "'='", "'<'", "'>'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "NAME", "FILTERVALUE", "TEXT", "SPACE" ]

    RULE_parse = 0
    RULE_interfaceSpec = 1
    RULE_methodSig = 2
    RULE_parameters = 3
    RULE_inputs = 4
    RULE_outputs = 5
    RULE_qualifiedtype = 6
    RULE_simpletype = 7
    RULE_arraytype = 8
    RULE_namedparam = 9
    RULE_typeparam = 10
    RULE_filter = 11

    ruleNames =  [ "parse", "interfaceSpec", "methodSig", "parameters", 
                   "inputs", "outputs", "qualifiedtype", "simpletype", "arraytype", 
                   "namedparam", "typeparam", "filter" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    T__4=5
    T__5=6
    T__6=7
    T__7=8
    T__8=9
    T__9=10
    T__10=11
    NAME=12
    FILTERVALUE=13
    TEXT=14
    SPACE=15

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class ParseContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(LQLParser.EOF, 0)

        def interfaceSpec(self):
            return self.getTypedRuleContext(LQLParser.InterfaceSpecContext,0)


        def filter_(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(LQLParser.FilterContext)
            else:
                return self.getTypedRuleContext(LQLParser.FilterContext,i)


        def getRuleIndex(self):
            return LQLParser.RULE_parse

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParse" ):
                listener.enterParse(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParse" ):
                listener.exitParse(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitParse" ):
                return visitor.visitParse(self)
            else:
                return visitor.visitChildren(self)




    def parse(self):

        localctx = LQLParser.ParseContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_parse)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 25
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==12:
                self.state = 24
                self.interfaceSpec()


            self.state = 30
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==13:
                self.state = 27
                self.filter_()
                self.state = 32
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 33
            self.match(LQLParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class InterfaceSpecContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NAME(self):
            return self.getToken(LQLParser.NAME, 0)

        def methodSig(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(LQLParser.MethodSigContext)
            else:
                return self.getTypedRuleContext(LQLParser.MethodSigContext,i)


        def getRuleIndex(self):
            return LQLParser.RULE_interfaceSpec

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterInterfaceSpec" ):
                listener.enterInterfaceSpec(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitInterfaceSpec" ):
                listener.exitInterfaceSpec(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitInterfaceSpec" ):
                return visitor.visitInterfaceSpec(self)
            else:
                return visitor.visitChildren(self)




    def interfaceSpec(self):

        localctx = LQLParser.InterfaceSpecContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_interfaceSpec)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 35
            self.match(LQLParser.NAME)
            self.state = 36
            self.match(LQLParser.T__0)
            self.state = 40
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==12:
                self.state = 37
                self.methodSig()
                self.state = 42
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 43
            self.match(LQLParser.T__1)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class MethodSigContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NAME(self):
            return self.getToken(LQLParser.NAME, 0)

        def inputs(self):
            return self.getTypedRuleContext(LQLParser.InputsContext,0)


        def outputs(self):
            return self.getTypedRuleContext(LQLParser.OutputsContext,0)


        def getRuleIndex(self):
            return LQLParser.RULE_methodSig

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterMethodSig" ):
                listener.enterMethodSig(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitMethodSig" ):
                listener.exitMethodSig(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitMethodSig" ):
                return visitor.visitMethodSig(self)
            else:
                return visitor.visitChildren(self)




    def methodSig(self):

        localctx = LQLParser.MethodSigContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_methodSig)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 45
            self.match(LQLParser.NAME)
            self.state = 59
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,6,self._ctx)
            if la_ == 1:
                self.state = 46
                self.match(LQLParser.T__2)
                self.state = 48
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==12:
                    self.state = 47
                    self.inputs()


                self.state = 50
                self.match(LQLParser.T__3)
                self.state = 52
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,4,self._ctx)
                if la_ == 1:
                    self.state = 51
                    self.outputs()


                pass

            elif la_ == 2:
                self.state = 54
                self.match(LQLParser.T__2)
                self.state = 56
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==12:
                    self.state = 55
                    self.inputs()


                self.state = 58
                self.match(LQLParser.T__4)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ParametersContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def simpletype(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(LQLParser.SimpletypeContext)
            else:
                return self.getTypedRuleContext(LQLParser.SimpletypeContext,i)


        def qualifiedtype(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(LQLParser.QualifiedtypeContext)
            else:
                return self.getTypedRuleContext(LQLParser.QualifiedtypeContext,i)


        def arraytype(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(LQLParser.ArraytypeContext)
            else:
                return self.getTypedRuleContext(LQLParser.ArraytypeContext,i)


        def namedparam(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(LQLParser.NamedparamContext)
            else:
                return self.getTypedRuleContext(LQLParser.NamedparamContext,i)


        def typeparam(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(LQLParser.TypeparamContext)
            else:
                return self.getTypedRuleContext(LQLParser.TypeparamContext,i)


        def getRuleIndex(self):
            return LQLParser.RULE_parameters

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParameters" ):
                listener.enterParameters(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParameters" ):
                listener.exitParameters(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitParameters" ):
                return visitor.visitParameters(self)
            else:
                return visitor.visitChildren(self)




    def parameters(self):

        localctx = LQLParser.ParametersContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_parameters)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 66
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,7,self._ctx)
            if la_ == 1:
                self.state = 61
                self.simpletype()
                pass

            elif la_ == 2:
                self.state = 62
                self.qualifiedtype()
                pass

            elif la_ == 3:
                self.state = 63
                self.arraytype()
                pass

            elif la_ == 4:
                self.state = 64
                self.namedparam()
                pass

            elif la_ == 5:
                self.state = 65
                self.typeparam()
                pass


            self.state = 78
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==6:
                self.state = 68
                self.match(LQLParser.T__5)
                self.state = 74
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,8,self._ctx)
                if la_ == 1:
                    self.state = 69
                    self.simpletype()
                    pass

                elif la_ == 2:
                    self.state = 70
                    self.qualifiedtype()
                    pass

                elif la_ == 3:
                    self.state = 71
                    self.arraytype()
                    pass

                elif la_ == 4:
                    self.state = 72
                    self.namedparam()
                    pass

                elif la_ == 5:
                    self.state = 73
                    self.typeparam()
                    pass


                self.state = 80
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class InputsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def parameters(self):
            return self.getTypedRuleContext(LQLParser.ParametersContext,0)


        def getRuleIndex(self):
            return LQLParser.RULE_inputs

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterInputs" ):
                listener.enterInputs(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitInputs" ):
                listener.exitInputs(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitInputs" ):
                return visitor.visitInputs(self)
            else:
                return visitor.visitChildren(self)




    def inputs(self):

        localctx = LQLParser.InputsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_inputs)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 81
            self.parameters()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class OutputsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def parameters(self):
            return self.getTypedRuleContext(LQLParser.ParametersContext,0)


        def getRuleIndex(self):
            return LQLParser.RULE_outputs

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOutputs" ):
                listener.enterOutputs(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOutputs" ):
                listener.exitOutputs(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitOutputs" ):
                return visitor.visitOutputs(self)
            else:
                return visitor.visitChildren(self)




    def outputs(self):

        localctx = LQLParser.OutputsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_outputs)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 83
            self.parameters()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class QualifiedtypeContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NAME(self, i:int=None):
            if i is None:
                return self.getTokens(LQLParser.NAME)
            else:
                return self.getToken(LQLParser.NAME, i)

        def getRuleIndex(self):
            return LQLParser.RULE_qualifiedtype

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterQualifiedtype" ):
                listener.enterQualifiedtype(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitQualifiedtype" ):
                listener.exitQualifiedtype(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitQualifiedtype" ):
                return visitor.visitQualifiedtype(self)
            else:
                return visitor.visitChildren(self)




    def qualifiedtype(self):

        localctx = LQLParser.QualifiedtypeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_qualifiedtype)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 85
            self.match(LQLParser.NAME)
            self.state = 90
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==7:
                self.state = 86
                self.match(LQLParser.T__6)
                self.state = 87
                self.match(LQLParser.NAME)
                self.state = 92
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SimpletypeContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NAME(self):
            return self.getToken(LQLParser.NAME, 0)

        def getRuleIndex(self):
            return LQLParser.RULE_simpletype

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSimpletype" ):
                listener.enterSimpletype(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSimpletype" ):
                listener.exitSimpletype(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSimpletype" ):
                return visitor.visitSimpletype(self)
            else:
                return visitor.visitChildren(self)




    def simpletype(self):

        localctx = LQLParser.SimpletypeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_simpletype)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 93
            self.match(LQLParser.NAME)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ArraytypeContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def simpletype(self):
            return self.getTypedRuleContext(LQLParser.SimpletypeContext,0)


        def qualifiedtype(self):
            return self.getTypedRuleContext(LQLParser.QualifiedtypeContext,0)


        def getRuleIndex(self):
            return LQLParser.RULE_arraytype

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterArraytype" ):
                listener.enterArraytype(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitArraytype" ):
                listener.exitArraytype(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitArraytype" ):
                return visitor.visitArraytype(self)
            else:
                return visitor.visitChildren(self)




    def arraytype(self):

        localctx = LQLParser.ArraytypeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_arraytype)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 97
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,11,self._ctx)
            if la_ == 1:
                self.state = 95
                self.simpletype()
                pass

            elif la_ == 2:
                self.state = 96
                self.qualifiedtype()
                pass


            self.state = 102
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==8:
                self.state = 99
                self.match(LQLParser.T__7)
                self.state = 104
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class NamedparamContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NAME(self):
            return self.getToken(LQLParser.NAME, 0)

        def simpletype(self):
            return self.getTypedRuleContext(LQLParser.SimpletypeContext,0)


        def qualifiedtype(self):
            return self.getTypedRuleContext(LQLParser.QualifiedtypeContext,0)


        def arraytype(self):
            return self.getTypedRuleContext(LQLParser.ArraytypeContext,0)


        def getRuleIndex(self):
            return LQLParser.RULE_namedparam

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNamedparam" ):
                listener.enterNamedparam(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNamedparam" ):
                listener.exitNamedparam(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitNamedparam" ):
                return visitor.visitNamedparam(self)
            else:
                return visitor.visitChildren(self)




    def namedparam(self):

        localctx = LQLParser.NamedparamContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_namedparam)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 105
            self.match(LQLParser.NAME)
            self.state = 106
            self.match(LQLParser.T__8)
            self.state = 110
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,13,self._ctx)
            if la_ == 1:
                self.state = 107
                self.simpletype()
                pass

            elif la_ == 2:
                self.state = 108
                self.qualifiedtype()
                pass

            elif la_ == 3:
                self.state = 109
                self.arraytype()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class TypeparamContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def simpletype(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(LQLParser.SimpletypeContext)
            else:
                return self.getTypedRuleContext(LQLParser.SimpletypeContext,i)


        def qualifiedtype(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(LQLParser.QualifiedtypeContext)
            else:
                return self.getTypedRuleContext(LQLParser.QualifiedtypeContext,i)


        def typeparam(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(LQLParser.TypeparamContext)
            else:
                return self.getTypedRuleContext(LQLParser.TypeparamContext,i)


        def getRuleIndex(self):
            return LQLParser.RULE_typeparam

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTypeparam" ):
                listener.enterTypeparam(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTypeparam" ):
                listener.exitTypeparam(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitTypeparam" ):
                return visitor.visitTypeparam(self)
            else:
                return visitor.visitChildren(self)




    def typeparam(self):

        localctx = LQLParser.TypeparamContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_typeparam)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 114
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,14,self._ctx)
            if la_ == 1:
                self.state = 112
                self.simpletype()
                pass

            elif la_ == 2:
                self.state = 113
                self.qualifiedtype()
                pass


            self.state = 116
            self.match(LQLParser.T__9)
            self.state = 120
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,15,self._ctx)
            if la_ == 1:
                self.state = 117
                self.simpletype()
                pass

            elif la_ == 2:
                self.state = 118
                self.qualifiedtype()
                pass

            elif la_ == 3:
                self.state = 119
                self.typeparam()
                pass


            self.state = 130
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==6:
                self.state = 122
                self.match(LQLParser.T__5)
                self.state = 126
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,16,self._ctx)
                if la_ == 1:
                    self.state = 123
                    self.simpletype()
                    pass

                elif la_ == 2:
                    self.state = 124
                    self.qualifiedtype()
                    pass

                elif la_ == 3:
                    self.state = 125
                    self.typeparam()
                    pass


                self.state = 132
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 133
            self.match(LQLParser.T__10)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class FilterContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def FILTERVALUE(self):
            return self.getToken(LQLParser.FILTERVALUE, 0)

        def getRuleIndex(self):
            return LQLParser.RULE_filter

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFilter" ):
                listener.enterFilter(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFilter" ):
                listener.exitFilter(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitFilter" ):
                return visitor.visitFilter(self)
            else:
                return visitor.visitChildren(self)




    def filter_(self):

        localctx = LQLParser.FilterContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_filter)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 135
            self.match(LQLParser.FILTERVALUE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





