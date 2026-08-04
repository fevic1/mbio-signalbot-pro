from __future__ import annotations

import logging
from typing import List, Dict, Any

from .models import EvidenceCategory, IntelligenceReport
from .collector import MarketCollector
from .verification import MarketVerifier
from .analyzer import MarketAnalyzer
from .scorer import MarketScorer
from .report import MarketReporter

logger = logging.getLogger(__name__)


class MarketIntelligenceEngine:
    """
    Market Intelligence Orchestrator.
    
    Wires the 5-layer intelligence pipeline into a single, cohesive execution flow.
    
    Pipeline Flow:
    1. Collector: Raw tool results -> RawEvidence
    2. Verifier: RawEvidence -> VerifiedEvidence (deduplication, scoring)
    3. Analyzer: VerifiedEvidence -> IntelligenceEvidence (insights, impact)
    4. Scorer: IntelligenceEvidence -> IntelligenceScore (dimensions, priority)
    5. Reporter: IntelligenceEvidence + Score -> IntelligenceReport (final output)
    
    Constraints:
    - Pure orchestration; contains zero business logic.
    - Strictly enforces the immutable data contracts between layers.
    """

    def __init__(self):
        self.collector = MarketCollector()
        self.verifier = MarketVerifier()
        self.analyzer = MarketAnalyzer()
        self.scorer = MarketScorer()
        self.reporter = MarketReporter()

    def process(
        self,
        asset: str,
        category: EvidenceCategory,
        tool_results: List[Dict[str, Any]],
    ) -> IntelligenceReport:
        """
        Executes the full 5-layer intelligence pipeline.
        """
        # Layer 1: Collection
        raw_evidence = self.collector.collect(asset, category, tool_results)
        
        # Layer 2: Verification
        verified_evidence = self.verifier.verify(raw_evidence)
        
        # Layer 3: Analysis
        intelligence = self.analyzer.analyze(verified_evidence)
        
        # Layer 4: Scoring
        score = self.scorer.score(intelligence)
        
        # Layer 5: Reporting
        report = self.reporter.generate(asset, intelligence, score)
        
        return report
