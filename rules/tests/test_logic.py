from django.test import TestCase

from ..logic import get_jsonlogic, has_valid_tokens, has_valid_left_parens, has_valid_right_parens, has_balanced_parens
from ..logic import has_valid_and_or, has_valid_not, has_valid_number_args, is_valid_logic_string

class TestGetJSONLogicDict(TestCase):

   def test_1(self):
      test_string = "((1 AND NOT 2) OR (3 AND (4 OR 5)))"
      jsonlogic = { "OR": [
                     {"AND": 
                        [ 
                         {"OR":
                           ["@5", 
                            "@4",
                           ]
                         },
                         "@3",
                        ]
                     },
                     {"AND": 
                        [ 
                         {"NOT": 
                           ["@2",]
                         },
                         "@1",
                        ]
                     }
                  ]
               }
      self.assertEqual(get_jsonlogic(test_string), jsonlogic)

   def test_2(self):
      test_string = "NOT (1 AND 2 OR (3 AND 4))"
      jsonlogic = {
               "NOT": [
                  { "OR": [
                        {"AND": [
                           "@4",
                           "@3"
                        ]},
                        {"AND": [
                           "@2",
                           "@1"
                        ]},
                     ]
                  }
               ]
            }
      self.assertEqual(get_jsonlogic(test_string), jsonlogic)
   
   def test_3(self):
      test_string = "((( NOT (1) )))"
      jsonlogic = {
                  "NOT": [
                     "@1"
                  ]
      }
      self.assertEqual(get_jsonlogic(test_string), jsonlogic)
   
   def test_4(self):
      test_string = "1"
      self.assertEqual(get_jsonlogic(test_string), "@1")
   
   def test_imbalanced_parens_1(self):
      test_string = "(1 AND (2 OR 3)"
      with self.assertRaises(ValueError):
         get_jsonlogic(test_string)
   
   def test_imbalanced_parens_2(self):
      test_string = "(1 AND 2 OR 3))"
      with self.assertRaises(ValueError):
         get_jsonlogic(test_string)

class TestLogicStringValidation(TestCase):

   def setUp(self):

      # all_test_strings[n][0] is the test string
      # all_test_strings[n][1] is the number of arguments in the string
      # all_test_strings[n][2] is the boolean result for whether the string is valid via is_valid_logic_string(test_string)
      self.all_test_strings = [
         ["((1 AND NOT 2) OR (3 AND (4 OR 5)))", 5, True],
         ["A AND (NOT 2 AND 3)", 3, False],
         ["1 AND (NOT whatever AND 3)", 3, False],
         ["1 WAND 2", 2, False],
         ["(( 1 AND   NOT  2)   OR (       3 AND   (4   OR    5))  )", 5, True],
         ["(((1 OR 2)))", 2, True],
         ["(((1OR2)))", 2, True],
         ["1 AND 2", 2, True],
         ["(AND NOT 2) OR 3", 3, False],
         ["(OR NOT 2) OR 3", 3, False],
         ["() OR 3", 3, False],
         ["1 (2 AND 3)", 3, False],
         ["(1 AND 2) OR NOT (3 (4))", 4, False],
         ["1 OR ( OR 3)", 3, False],
         ["1 AND 2", 2, True],
         ["(1 AND 2) 3", 3, False],
         ["(1 AND 2)) 3", 3, False],
         ["(1 AND ) 3", 3, False],
         ["(1 OR ) 3", 3, False],
         ["NOT ) 1 AND 3", 3, False],
         ["1 AND OR 2", 2, False],
         ["(3 AND AND 2)", 3, False],
         ["(3 OR OR 2)", 3, False],
         ["NOT 1", 1, True],
         ["1 AND NOT (2 OR 3)", 3, True],
         ["1 AND 2 NOT 3", 3, False],
         ["1 AND (2 OR 3) NOT 4", 4, False],
         ["NOT AND (1 OR 2)", 2, False],
         ["NOT NOT 1", 1, False],
         ["NOT 1 NOT 2", 2, False],
         ["(1 OR 2) NOT", 2, False],
         ["((4 AND NOT 3) OR (2 AND (1 OR 5)))", 5, True],
         ["1 2 AND 3", 3, False],
         ["1 OR (2 3)", 3, False],
         ["1 AND (2 OR 3)", 2, False],
         ["0 AND 1", 2, False],
         ["13 AND 1", 2, False],
         ["1 AND (2 OR 3)", 4, False],
         ["1 AND (2 OR 4)", 4, False],
         ["1 AND 2 OR (3 AND (4 OR (5 AND 6)))", 6, True],
         ["((1 OR 2) AND 3 OR ((4 AND 1) OR (5 AND NOT (1 OR 6))))", 6, True],
         ["1 AND (2 OR 3", 3, False],
         ["1 AND 2 OR 3)", 3, False],
         ["(1 AND 2 OR 3", 3, False],
         ["((1 AND 2) OR 3", 3, False],
         ["1 AND (2 OR 3))", 3, False],
         ["((1 OR 2) AND 3 OR ((4 AND 1) OR (5 AND NOT (1 OR 6)))", 6, False],
         ["1", 1, True]
      ]

   def test_has_valid_tokens_true_1(self):
      test_string = "((1 AND NOT 2) OR (3 AND (4 OR 5)))"
      self.assertEqual(has_valid_tokens(test_string), True)
   
   def test_has_valid_tokens_false_1(self):
      test_string = "A AND (NOT 2 AND 3)"
      self.assertEqual(has_valid_tokens(test_string), False)
   
   def test_has_valid_tokens_false_2(self):
      test_string = "1 AND (NOT whatever AND 3)"
      self.assertEqual(has_valid_tokens(test_string), False)

   def test_has_valid_tokens_false_3(self):
      test_string = "1 WAND 2"
      self.assertEqual(has_valid_tokens(test_string), False)
   
   def test_has_valid_left_parens_true_1(self):
      test_string = "((1 AND NOT 2) OR (3 AND (4 OR 5)))"
      self.assertEqual(has_valid_left_parens(test_string), True)
   
   def test_has_valid_left_parens_true_2(self):
      test_string = "(( 1 AND   NOT  2)   OR (       3 AND   (4   OR    5))  )"
      self.assertEqual(has_valid_left_parens(test_string), True)
   
   def test_has_valid_left_parens_true_3(self):
      test_string = "(((1 OR 2)))"
      self.assertEqual(has_valid_left_parens(test_string), True)
   
   def test_has_valid_left_parens_true_4(self):
      test_string = "(((1OR2)))"
      self.assertEqual(has_valid_left_parens(test_string), True)
   
   def test_has_valid_left_parens_true_5(self):
      test_string = "1 AND 2"
      self.assertEqual(has_valid_left_parens(test_string), True)

   def test_has_valid_left_parens_false_1(self):
      test_string = "(AND NOT 2) OR 3"
      self.assertEqual(has_valid_left_parens(test_string), False)
   
   def test_has_valid_left_parens_false_2(self):
      test_string = "(OR NOT 2) OR 3"
      self.assertEqual(has_valid_left_parens(test_string), False)
   
   def test_has_valid_left_parens_false_3(self):
      test_string = "() OR 3"
      self.assertEqual(has_valid_left_parens(test_string), False)
   
   def test_has_valid_left_parens_false_4(self):
      test_string = "1 (2 AND 3)"
      self.assertEqual(has_valid_left_parens(test_string), False)
   
   def test_has_valid_left_parens_false_4(self):
      test_string = "(1 AND 2) OR NOT (3 (4))"
      self.assertEqual(has_valid_left_parens(test_string), False)
   
   def test_has_valid_left_parens_false_5(self):
      test_string = "1 OR ( OR 3)"
      self.assertEqual(has_valid_left_parens(test_string), False)
   
   def test_has_valid_right_parens_true_1(self):
      test_string = "((1 AND NOT 2) OR (3 AND (4 OR 5)))"
      self.assertEqual(has_valid_right_parens(test_string), True)
   
   def test_has_valid_right_parens_true_2(self):
      test_string = "(((1 OR 2)))"
      self.assertEqual(has_valid_right_parens(test_string), True)
   
   def test_has_valid_right_parens_true_3(self):
      test_string = "(((1OR2)))"
      self.assertEqual(has_valid_right_parens(test_string), True)
   
   def test_has_valid_right_parens_true_4(self):
      test_string = "1 AND 2"
      self.assertEqual(has_valid_right_parens(test_string), True)
   
   def test_has_valid_right_parens_false_1(self):
      test_string = "(1 AND 2) 3"
      self.assertEqual(has_valid_right_parens(test_string), False)
   
   def test_has_valid_right_parens_false_2(self):
      test_string = "(1 AND 2)) 3"
      self.assertEqual(has_valid_right_parens(test_string), False)
   
   def test_has_valid_right_parens_false_3(self):
      test_string = "(1 AND ) 3"
      self.assertEqual(has_valid_right_parens(test_string), False)
   
   def test_has_valid_right_parens_false_4(self):
      test_string = "(1 OR ) 3"
      self.assertEqual(has_valid_right_parens(test_string), False)
   
   def test_has_valid_right_parens_false_5(self):
      test_string = "NOT ) 1 AND 3"
      self.assertEqual(has_valid_right_parens(test_string), False)
   
   def test_has_valid_and_or_true_1(self):
      test_string = "((1 AND NOT 2) OR (3 AND (4 OR 5)))"
      self.assertEqual(has_valid_and_or(test_string), True)
   
   def test_has_valid_and_or_false_1(self):
      test_string = "1 AND OR 2"
      self.assertEqual(has_valid_and_or(test_string), False)
   
   def test_has_valid_and_or_false_2(self):
      test_string = "(3 AND AND 2)"
      self.assertEqual(has_valid_and_or(test_string), False)
   
   def test_has_valid_and_or_false_3(self):
      test_string = "(3 OR AND 2)"
      self.assertEqual(has_valid_and_or(test_string), False)
   
   def test_has_valid_and_or_false_4(self):
      test_string = "(3 OR OR 2)"
      self.assertEqual(has_valid_and_or(test_string), False)
   
   def test_has_valid_not_true_1(self):
      test_string = "NOT 1"
      self.assertEqual(has_valid_not(test_string), True)
   
   def test_has_valid_not_true_2(self):
      test_string = "1 AND NOT (2 OR 3)"
      self.assertEqual(has_valid_not(test_string), True)
   
   def test_has_valid_not_true_3(self):
      test_string = "1 AND 2"
      self.assertEqual(has_valid_not(test_string), True)
   
   def test_has_valid_not_false_1(self):
      test_string = "1 AND 2 NOT 3"
      self.assertEqual(has_valid_not(test_string), False)
   
   def test_has_valid_not_false_2(self):
      test_string = "1 AND (2 OR 3) NOT 4"
      self.assertEqual(has_valid_not(test_string), False)
   
   def test_has_valid_not_false_3(self):
      test_string = "NOT AND (1 OR 2)"
      self.assertEqual(has_valid_not(test_string), False)
   
   def test_has_valid_not_false_4(self):
      test_string = "NOT NOT 1"
      self.assertEqual(has_valid_not(test_string), False)
   
   def test_has_valid_not_false_4(self):
      test_string = "NOT 1 NOT 2"
      self.assertEqual(has_valid_not(test_string), False)
   
   def test_has_valid_not_false_5(self):
      test_string = "(1 OR 2) NOT"
      self.assertEqual(has_valid_not(test_string), False)
   
   def test_has_valid_number_args_true_1(self):
      test_string = "((1 AND NOT 2) OR (3 AND (4 OR 5)))"
      self.assertEqual(has_valid_number_args(test_string, 5), True)
   
   def test_has_valid_number_args_true_2(self):
      test_string = "((4 AND NOT 3) OR (2 AND (1 OR 5)))"
      self.assertEqual(has_valid_number_args(test_string, 5), True)
   
   def test_has_valid_number_args_true_3(self):
      test_string = "((1 OR 2) AND 3 OR ((4 AND 1) OR (5 AND NOT (1 OR 6))))"
      self.assertEqual(has_valid_number_args(test_string, 6), True)
   
   def test_has_valid_number_args_false_1(self):
      test_string = "1 2 AND 3"
      self.assertEqual(has_valid_number_args(test_string, 3), False)
   
   def test_has_valid_number_args_false_2(self):
      test_string = "1 OR (2 3)"
      self.assertEqual(has_valid_number_args(test_string, 3), False)
   
   def test_has_valid_number_args_false_3(self):
      test_string = "1 AND (2 OR 3)"
      self.assertEqual(has_valid_number_args(test_string, 2), False)
   
   def test_has_valid_number_args_false_4(self):
      test_string = "0 AND 1"
      self.assertEqual(has_valid_number_args(test_string, 2), False)
   
   def test_has_valid_number_args_false_5(self):
      test_string = "13 AND 1"
      self.assertEqual(has_valid_number_args(test_string, 2), False)
   
   def test_has_valid_number_args_false_6(self):
      test_string = "1 AND (2 OR 3)"
      self.assertEqual(has_valid_number_args(test_string, 4), False)
   
   def test_has_valid_number_args_false_7(self):
      test_string = "1 AND (2 OR 4)"
      self.assertEqual(has_valid_number_args(test_string, 4), False)
   
   def test_has_balanced_parens_true_1(self):
      test_string = "1 AND 2 OR (3 AND (4 OR (5 AND 6)))"
      self.assertEqual(has_balanced_parens(test_string), True)
   
   def test_has_balanced_parens_true_2(self):
      test_string = "((1 OR 2) AND 3 OR ((4 AND 1) OR (5 AND NOT (1 OR 6))))"
      self.assertEqual(has_balanced_parens(test_string), True)

   def test_has_balanced_parens_false_1(self):
      test_string = "1 AND (2 OR 3"
      self.assertEqual(has_balanced_parens(test_string), False)
   
   def test_has_balanced_parens_false_2(self):
      test_string = "1 AND 2 OR 3)"
      self.assertEqual(has_balanced_parens(test_string), False)
   
   def test_has_balanced_parens_false_3(self):
      test_string = "(1 AND 2 OR 3"
      self.assertEqual(has_balanced_parens(test_string), False)
   
   def test_has_balanced_parens_false_4(self):
      test_string = "((1 AND 2) OR 3"
      self.assertEqual(has_balanced_parens(test_string), False)
   
   def test_has_balanced_parens_false_5(self):
      test_string = "1 AND (2 OR 3))"
      self.assertEqual(has_balanced_parens(test_string), False)
   
   def test_has_balanced_parens_false_6(self):
      test_string = "((1 OR 2) AND 3 OR ((4 AND 1) OR (5 AND NOT (1 OR 6)))"
      self.assertEqual(has_balanced_parens(test_string), False)

   def test_is_valid_logic_string(self):
      for count,group in enumerate(self.all_test_strings):
         test_string = group[0]
         num_args = group[1]
         result = group[2]
         self.assertEqual(is_valid_logic_string(test_string, num_args), result)