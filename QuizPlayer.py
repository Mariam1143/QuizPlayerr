import json
import time
import os
import sys

class Question:
    def __init__(self, question_text, choices, correct_choice_index, category="General", difficulty="Medium"):
        self.question_text = question_text
        self.choices = choices
        self.correct_choice_index = correct_choice_index
        self.category = category
        self.difficulty = difficulty

    def is_correct(self, choice_index):
        return choice_index == self.correct_choice_index

    def to_dict(self):
        return {
            'question_text': self.question_text,
            'choices': self.choices,
            'correct_choice_index': self.correct_choice_index,
            'category': self.category,
            'difficulty': self.difficulty
        }

    @staticmethod
    def from_dict(data):
        return Question(
            data['question_text'],
            data['choices'],
            data['correct_choice_index'],
            data.get('category', 'General'),
            data.get('difficulty', 'Medium')
        )

class Quiz:
    def __init__(self, questions):
        self.questions = questions
        self.score = 0
        self.start_time = None
        self.end_time = None
        self.responses = []  # For storing user's answers and times

    def start(self):
        print("\nStarting the quiz. Good luck!\n")
        self.score = 0
        self.start_time = time.time()
        for idx, question in enumerate(self.questions, start=1):
            print(f"Question {idx}: ({question.category} / {question.difficulty})")
            print(question.question_text)
            for i, choice in enumerate(question.choices):
                print(f"  {i + 1}. {choice}")
            user_choice = self.get_user_choice(len(question.choices))
            correct = question.is_correct(user_choice - 1)
            if correct:
                print("Correct!\n")
                self.score += 1
            else:
                correct_answer = question.choices[question.correct_choice_index]
                print(f"Wrong! The correct answer was: {correct_answer}\n")
            self.responses.append({'question': question.question_text, 'user_choice': user_choice,
                                   'correct_choice': question.correct_choice_index + 1, 'correct': correct})
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        print(f"Quiz completed! Your score: {self.score} out of {len(self.questions)}")
        print(f"Total time taken: {duration:.2f} seconds")

    @staticmethod
    def get_user_choice(num_choices):
        while True:
            try:
                choice = input("Your answer (number): ").strip()
                if choice.lower() == 'q':
                    print("Quiz aborted by user.")
                    sys.exit(0)
                choice_int = int(choice)
                if 1 <= choice_int <= num_choices:
                    return choice_int
                else:
                    print(f"Please enter a number between 1 and {num_choices}, or 'q' to quit.")
            except ValueError:
                print(f"Invalid input. Enter a number between 1 and {num_choices}, or 'q' to quit.")

class QuizManager:
    DATA_FILE = "quiz_data.json"
    STATS_FILE = "quiz_stats.json"

    def __init__(self):
        self.questions = []
        self.load_questions()
        self.stats = self.load_stats()

    def load_questions(self):
        if os.path.exists(self.DATA_FILE):
            try:
                with open(self.DATA_FILE, "r") as f:
                    data = json.load(f)
                    self.questions = [Question.from_dict(q) for q in data]
            except Exception:
                print("Warning: Failed to load questions, starting with empty question bank.")
                self.questions = []
        else:
            self.questions = []

    def save_questions(self):
        data = [q.to_dict() for q in self.questions]
        try:
            with open(self.DATA_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving questions: {e}")

    def load_stats(self):
        if os.path.exists(self.STATS_FILE):
            try:
                with open(self.STATS_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                return {"quizzes_taken": 0, "total_score": 0, "total_questions": 0, "total_time": 0.0}
        else:
            return {"quizzes_taken": 0, "total_score": 0, "total_questions": 0, "total_time": 0.0}

    def save_stats(self):
        try:
            with open(self.STATS_FILE, "w") as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            print(f"Error saving stats: {e}")

    def add_question(self):
        print("\nAdd a new question")
        question_text = input("Enter the question text: ").strip()
        choices = []
        while True:
            choice = input(f"Enter choice {len(choices)+1} (or just press ENTER to finish): ").strip()
            if choice == '' and len(choices) >= 2:
                break
            elif choice == '':
                print("Please enter at least two choices.")
                continue
            choices.append(choice)
        while True:
            correct_choice = input(f"Enter the number of the correct choice (1-{len(choices)}): ").strip()
            try:
                correct_index = int(correct_choice) - 1
                if 0 <= correct_index < len(choices):
                    break
                else:
                    print("Invalid number, try again.")
            except ValueError:
                print("Please enter a valid number.")
        category = input("Enter question category (default General): ").strip()
        if not category:
            category = "General"
        difficulty = input("Enter difficulty (Easy, Medium, Hard - default Medium): ").strip().capitalize()
        if difficulty not in ["Easy", "Medium", "Hard"]:
            difficulty = "Medium"
        new_question = Question(question_text, choices, correct_index, category, difficulty)
        self.questions.append(new_question)
        self.save_questions()
        print("Question added successfully!")

    def edit_question(self):
        if not self.questions:
            print("No questions available to edit.")
            return
        self.list_questions()
        index = self.get_question_index("edit")
        if index is None:
            return
        q = self.questions[index]
        print(f"\nEditing Question #{index + 1}")
        print(f"Current text: {q.question_text}")
        new_text = input("Enter new text (or press ENTER to keep current): ").strip()
        if new_text:
            q.question_text = new_text
        print("Current choices:")
        for i, c in enumerate(q.choices, 1):
            print(f"{i}. {c}")
        while True:
            choice_edit = input("Edit choices? (y/n): ").strip().lower()
            if choice_edit == 'y':
                q.choices = []
                while True:
                    choice = input(f"Enter choice {len(q.choices)+1} (or just press ENTER to finish): ").strip()
                    if choice == '' and len(q.choices) >= 2:
                        break
                    elif choice == '':
                        print("Please enter at least two choices.")
                        continue
                    q.choices.append(choice)
                while True:
                    correct_choice = input(f"Enter the number of the correct choice (1-{len(q.choices)}): ").strip()
                    try:
                        correct_index = int(correct_choice) - 1
                        if 0 <= correct_index < len(q.choices):
                            q.correct_choice_index = correct_index
                            break
                        else:
                            print("Invalid number, try again.")
                    except ValueError:
                        print("Please enter a valid number.")
                break
            elif choice_edit == 'n':
                break
            else:
                print("Please enter 'y' or 'n'.")
        new_category = input(f"Enter new category (current: {q.category}) or press ENTER to keep: ").strip()
        if new_category:
            q.category = new_category
        new_difficulty = input(f"Enter new difficulty (Easy, Medium, Hard) (current: {q.difficulty}) or press ENTER to keep: ").strip().capitalize()
        if new_difficulty in ["Easy", "Medium", "Hard"]:
            q.difficulty = new_difficulty
        self.save_questions()
        print("Question updated successfully!")

    def delete_question(self):
        if not self.questions:
            print("No questions available to delete.")
            return
        self.list_questions()
        index = self.get_question_index("delete")
        if index is None:
            return
        q = self.questions.pop(index)
        self.save_questions()
        print(f"Deleted question: {q.question_text}")

    def list_questions(self):
        if not self.questions:
            print("\nNo questions available.")
            return
        print("\nQuestions:")
        for i, q in enumerate(self.questions, 1):
            print(f"{i}. {q.question_text} (Category: {q.category}, Difficulty: {q.difficulty})")

    def get_question_index(self, action):
        while True:
            idx = input(f"Enter the number of the question to {action} (or 'c' to cancel): ").strip()
            if idx.lower() == 'c':
                return None
            try:
                index = int(idx) - 1
                if 0 <= index < len(self.questions):
                    return index
                else:
                    print(f"Please enter a number between 1 and {len(self.questions)}.")
            except ValueError:
                print("Invalid input. Please enter a valid number or 'c' to cancel.")

    def run_quiz(self):
        if not self.questions:
            print("No questions to play. Please add questions first.")
            return
        print("\nChoose category or press ENTER for all categories:")
        categories = sorted(set(q.category for q in self.questions))
        for i, cat in enumerate(categories, start=1):
            print(f"{i}. {cat}")
        cat_choice = input("Your choice: ").strip()
        if cat_choice:
            try:
                cat_index = int(cat_choice) - 1
                if 0 <= cat_index < len(categories):
                    selected_category = categories[cat_index]
                else:
                    print("Invalid category choice, using all categories.")
                    selected_category = None
            except ValueError:
                print("Invalid input, using all categories.")
                selected_category = None
        else:
            selected_category = None
        filtered_questions = [q for q in self.questions if selected_category is None or q.category == selected_category]
        # Shuffle questions for randomness
        import random
        random.shuffle(filtered_questions)
        quiz = Quiz(filtered_questions)
        quiz.start()
        # Update stats
        self.stats['quizzes_taken'] += 1
        self.stats['total_score'] += quiz.score
        self.stats['total_questions'] += len(filtered_questions)
        self.stats['total_time'] += (quiz.end_time - quiz.start_time) if quiz.end_time and quiz.start_time else 0
        self.save_stats()

    def view_stats(self):
        print("\nQuiz Statistics:")
        qt = self.stats.get('quizzes_taken',0)
        if qt ==0:
            print("No quizzes taken yet.")
            return
        total_score = self.stats.get('total_score',0)
        total_questions = self.stats.get('total_questions',0)
        total_time = self.stats.get('total_time',0.0)
        avg_score_pct = (total_score/total_questions)*100 if total_questions else 0
        avg_time_per_question = (total_time/total_questions) if total_questions else 0
        print(f"Total quizzes taken: {qt}")
        print(f"Total questions answered: {total_questions}")
        print(f"Average score: {avg_score_pct:.2f}%")
        print(f"Average time per question: {avg_time_per_question:.2f} seconds")

    def main_menu(self):
        while True:
            print("\n--- Quiz Generator & Player ---")
            print("1. Add Question")
            print("2. Edit Question")
            print("3. Delete Question")
            print("4. List All Questions")
            print("5. Take a Quiz")
            print("6. View Statistics")
            print("7. Exit")
            choice = input("Choose an option: ").strip()
            if choice == '1':
                self.add_question()
            elif choice == '2':
                self.edit_question()
            elif choice == '3':
                self.delete_question()
            elif choice == '4':
                self.list_questions()
            elif choice == '5':
                self.run_quiz()
            elif choice == '6':
                self.view_stats()
            elif choice == '7':
                print("Goodbye!")
                break
            else:
                print("Invalid choice, please try again.")

def main():
    manager = QuizManager()
    manager.main_menu()

if __name__ == "__main__":
    main()
