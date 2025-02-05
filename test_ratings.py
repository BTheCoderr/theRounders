import unittest
from datetime import datetime
from massey_ratings_base import Game
from elos_ratings import ElosRatings

class TestRatingMethods(unittest.TestCase):
    def setUp(self):
        """Setup test case from Example 4.2/6.2 in the paper."""
        self.teams = [
            "Beast Squares",
            "Gaussian Eliminators",
            "Likelihood Loggers",
            "Linear Aggressors"
        ]
        
        # Initialize both rating systems
        self.elos = ElosRatings(self.teams)
        
        # Add games from the example
        games = [
            ("Beast Squares", "Gaussian Eliminators", 10, 6),
            ("Likelihood Loggers", "Linear Aggressors", 4, 4),
            ("Linear Aggressors", "Gaussian Eliminators", 9, 2),
            ("Beast Squares", "Linear Aggressors", 8, 6),
            ("Gaussian Eliminators", "Likelihood Loggers", 3, 2)
        ]
        
        for team_a, team_b, score_a, score_b in games:
            game = Game(
                team_a=team_a,
                team_b=team_b,
                score_a=score_a,
                score_b=score_b,
                is_home_a=True,
                date=datetime.now()
            )
            self.elos.add_game(game)
    
    def test_binary_ratings(self):
        """Test binary ratings calculation."""
        # Test Beast Squares vs Gaussian Eliminators
        bij = self.elos.get_binary_rating("Beast Squares", "Gaussian Eliminators")
        self.assertAlmostEqual(bij, 1.0)  # BS won their only meeting
        
        # Test Likelihood Loggers vs Linear Aggressors
        bij = self.elos.get_binary_rating("Likelihood Loggers", "Linear Aggressors")
        self.assertAlmostEqual(bij, 0.5)  # They tied
    
    def test_elos_ratings(self):
        """Test Elos ratings from Example 6.2."""
        ratings = self.elos.calculate_ratings()
        
        # Check relative ordering matches paper
        expected_order = [
            "Beast Squares",
            "Linear Aggressors",
            "Gaussian Eliminators",
            "Likelihood Loggers"
        ]
        
        # Sort teams by rating
        sorted_teams = sorted(ratings.keys(), key=lambda t: ratings[t], reverse=True)
        self.assertEqual(sorted_teams, expected_order)
        
        # Check specific ratios from paper
        bs_rating = ratings["Beast Squares"]
        ll_rating = ratings["Likelihood Loggers"]
        ratio = bs_rating / ll_rating
        self.assertAlmostEqual(ratio, 1.316/0.864, places=2)
    
    def test_transition_matrix(self):
        """Test Markov chain transition matrix from paper."""
        Q = self.elos.calculate_transition_matrix()
        
        # Check matrix properties
        n_teams = len(self.teams)
        self.assertEqual(Q.shape, (n_teams, n_teams))
        
        # Check row sums are zero (property of Q matrix)
        row_sums = Q.sum(axis=1)
        for sum_i in row_sums:
            self.assertAlmostEqual(sum_i, 0)
        
        # Check equilibrium distribution
        p = self.elos.calculate_equilibrium_distribution()
        expected_p = [0.329, 0.154, 0.216, 0.301]  # From paper
        
        for team, prob in zip(self.teams, expected_p):
            self.assertAlmostEqual(p[team], prob, places=2)
    
    def test_anti_ratings(self):
        """Test anti-ratings calculation."""
        anti = self.elos.calculate_anti_ratings()
        
        # Beast Squares lost 0 games
        self.assertAlmostEqual(anti["Beast Squares"], 0.0)
        
        # Gaussian Eliminators lost 2 of 3 games
        self.assertAlmostEqual(anti["Gaussian Eliminators"], 2/3, places=2)
    
    def test_market_values(self):
        """Test economic interpretation."""
        values = self.elos.calculate_market_values()
        
        # Check relative values
        bs_value = values["Beast Squares"]
        ge_value = values["Gaussian Eliminators"]
        
        # Beast Squares should have higher market value
        self.assertGreater(bs_value, ge_value)
    
    def test_complete_analysis(self):
        """Test comprehensive analysis output."""
        analysis = self.elos.get_complete_analysis()
        
        # Check all metrics are present
        metrics = ['rating', 'anti_rating', 'market_value', 
                  'equilibrium_prob', 'combined_score']
        
        for team in self.teams:
            self.assertTrue(team in analysis)
            for metric in metrics:
                self.assertTrue(metric in analysis[team])
                
    def test_markov_properties(self):
        """Test Markov chain analysis."""
        props = self.elos.analyze_markov_properties()
        
        # Check required properties are present
        self.assertTrue('eigenvalues' in props)
        self.assertTrue('mixing_time' in props)
        self.assertTrue('stationary_distribution' in props)
        self.assertTrue('convergence_rate' in props)
        
        # Check eigenvalues
        if len(props['eigenvalues']) > 0:
            # Principal eigenvalue should be 0 (stochastic matrix)
            self.assertAlmostEqual(props['eigenvalues'][0].real, 0, places=6)
            
            # All other eigenvalues should have negative real parts
            for ev in props['eigenvalues'][1:]:
                self.assertLess(ev.real, 0)
        
        # Mixing time should be positive if defined
        if props['mixing_time'] is not None:
            self.assertGreater(props['mixing_time'], 0)
        
        # Convergence rate should be between 0 and 1 if defined
        if props['convergence_rate'] is not None:
            self.assertGreater(props['convergence_rate'], 0)
            self.assertLess(props['convergence_rate'], 1)
    
    def test_rating_confidence(self):
        """Test confidence interval calculations."""
        conf = self.elos.calculate_rating_confidence()
        
        for team in self.teams:
            team_conf = conf[team]
            
            # Check required fields
            self.assertTrue('rating' in team_conf)
            self.assertTrue('std_error' in team_conf)
            self.assertTrue('conf_interval' in team_conf)
            
            # Check confidence interval contains rating
            lower, upper = team_conf['conf_interval']
            self.assertLessEqual(lower, team_conf['rating'])
            self.assertGreaterEqual(upper, team_conf['rating'])
            
            # Check standard error is non-negative
            self.assertGreaterEqual(team_conf['std_error'], 0)
    
    def test_predictive_accuracy(self):
        """Test prediction accuracy metrics."""
        metrics = self.elos.calculate_predictive_accuracy()
        
        # Check required metrics
        self.assertTrue('accuracy' in metrics)
        self.assertTrue('mae_spread' in metrics)
        self.assertTrue('log_likelihood' in metrics)
        
        # Check ranges
        self.assertGreaterEqual(metrics['accuracy'], 0)
        self.assertLessEqual(metrics['accuracy'], 1)
        
        self.assertGreaterEqual(metrics['mae_spread'], 0)
        
        # Log likelihood should be negative (probabilities < 1)
        self.assertLessEqual(metrics['log_likelihood'], 0)
    
    def test_spread_prediction(self):
        """Test point spread predictions."""
        # Beast Squares vs Gaussian Eliminators
        # Actual margin was BS +4 (10-6)
        spread = self.elos.predict_spread("Beast Squares", "Gaussian Eliminators")
        
        # Predicted spread should be positive (BS favored)
        self.assertGreater(spread, 0)
        
        # For tied teams, spread should be close to 0
        spread = self.elos.predict_spread("Likelihood Loggers", "Linear Aggressors")
        self.assertAlmostEqual(abs(spread), 0, places=1)
    
if __name__ == '__main__':
    unittest.main() 