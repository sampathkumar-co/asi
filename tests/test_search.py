import unittest
from seed.search.architecture import AgentGenome, ArchitectureSearch

class SearchTests(unittest.TestCase):
    def test_genome_id_stable(self):
        self.assertEqual(AgentGenome().candidate_id, AgentGenome().candidate_id)

    def test_invalid_genome(self):
        with self.assertRaises(ValueError): AgentGenome(max_steps=0).validate()

    def test_search_archives_and_returns_candidate(self):
        def ev(g): return (0.5 + 0.01*g.max_steps, g.max_steps/10)
        s = ArchitectureSearch(ev, seed=1)
        best = s.search(AgentGenome(), generations=2, population=4)
        self.assertTrue(0 <= best.capability <= 2)
        self.assertGreaterEqual(len(s.archive), 1)

if __name__ == "__main__": unittest.main()
