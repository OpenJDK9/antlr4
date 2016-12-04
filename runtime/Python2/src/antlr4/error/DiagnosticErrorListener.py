#
# Copyright (c) 2012 The ANTLR Project Contributors. All rights reserved.
# Use of this file is governed by the BSD 3-clause license that
# can be found in the LICENSE.txt file in the project root.
#


#
# This implementation of {@link ANTLRErrorListener} can be used to identify
# certain potential correctness and performance problems in grammars. "Reports"
# are made by calling {@link Parser#notifyErrorListeners} with the appropriate
# message.
#
# <ul>
# <li><b>Ambiguities</b>: These are cases where more than one path through the
# grammar can match the input.</li>
# <li><b>Weak context sensitivity</b>: These are cases where full-context
# prediction resolved an SLL conflict to a unique alternative which equaled the
# minimum alternative of the SLL conflict.</li>
# <li><b>Strong (forced) context sensitivity</b>: These are cases where the
# full-context prediction resolved an SLL conflict to a unique alternative,
# <em>and</em> the minimum alternative of the SLL conflict was found to not be
# a truly viable alternative. Two-stage parsing cannot be used for inputs where
# this situation occurs.</li>
# </ul>

from io import StringIO
from antlr4.Utils import str_set
from antlr4.error.ErrorListener import ErrorListener

class DiagnosticErrorListener(ErrorListener):

    def __init__(self, exactOnly=True):
        # whether all ambiguities or only exact ambiguities are reported.
        self.exactOnly = exactOnly

    def reportAmbiguity(self, recognizer, dfa, startIndex,
                       stopIndex, exact, ambigAlts, configs):
        if self.exactOnly and not exact:
            return

        with StringIO() as buf:
            buf.write(u"reportAmbiguity d=")
            buf.write(self.getDecisionDescription(recognizer, dfa))
            buf.write(u": ambigAlts=")
            buf.write(str_set(self.getConflictingAlts(ambigAlts, configs)))
            buf.write(u", input='")
            buf.write(recognizer.getTokenStream().getText((startIndex, stopIndex)))
            buf.write(u"'")
            recognizer.notifyErrorListeners(buf.getvalue())


    def reportAttemptingFullContext(self, recognizer, dfa, startIndex,
                       stopIndex, conflictingAlts, configs):
        with StringIO() as buf:
            buf.write(u"reportAttemptingFullContext d=")
            buf.write(self.getDecisionDescription(recognizer, dfa))
            buf.write(u", input='")
            buf.write(recognizer.getTokenStream().getText((startIndex, stopIndex)))
            buf.write(u"'")
            recognizer.notifyErrorListeners(buf.getvalue())

    def reportContextSensitivity(self, recognizer, dfa, startIndex,
                       stopIndex, prediction, configs):
        with StringIO() as buf:
            buf.write(u"reportContextSensitivity d=")
            buf.write(self.getDecisionDescription(recognizer, dfa))
            buf.write(u", input='")
            buf.write(recognizer.getTokenStream().getText((startIndex, stopIndex)))
            buf.write(u"'")
            recognizer.notifyErrorListeners(buf.getvalue())

    def getDecisionDescription(self, recognizer, dfa):
        decision = dfa.decision
        ruleIndex = dfa.atnStartState.ruleIndex

        ruleNames = recognizer.ruleNames
        if ruleIndex < 0 or ruleIndex >= len(ruleNames):
            return unicode(decision)

        ruleName = ruleNames[ruleIndex]
        if ruleName is None or len(ruleName)==0:
            return unicode(decision)

        return unicode(decision) + u" (" + ruleName + u")"

    #
    # Computes the set of conflicting or ambiguous alternatives from a
    # configuration set, if that information was not already provided by the
    # parser.
    #
    # @param reportedAlts The set of conflicting or ambiguous alternatives, as
    # reported by the parser.
    # @param configs The conflicting or ambiguous configuration set.
    # @return Returns {@code reportedAlts} if it is not {@code null}, otherwise
    # returns the set of alternatives represented in {@code configs}.
    #
    def getConflictingAlts(self, reportedAlts, configs):
        if reportedAlts is not None:
            return reportedAlts

        result = set()
        for config in configs:
            result.add(config.alt)

        return result
