from django.db import models
from django.contrib.auth.models import User
from content.models import Lesson, Quiz

from django.db.models import Sum



class LessonProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title} - Completed: {self.is_completed}"

class QuizResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='quizzes')
    score = models.IntegerField()
    total_questions = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.lesson.title} - Score: {self.score}/{self.total_questions}"
    

class QuizAttempt(models.Model):
    """Model to track quiz attempts by users."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey('content.Quiz', on_delete=models.CASCADE)
    score = models.IntegerField()
    attempt_number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} (Attempt {self.attempt_number})"

class Leaderboard:
    """A utility to generate leaderboard rankings."""

    @staticmethod
    def generate_ranking():
        """Generate rankings based on total lessons completed and quiz scores."""
        users = User.objects.all()
        leaderboard = []

        for user in users:
            lessons_completed = LessonProgress.objects.filter(user=user, is_completed=True).count()
            total_score = QuizResult.objects.filter(user=user).aggregate(Sum('score'))['score__sum'] or 0

            leaderboard.append({
                'user': user,
                'lessons_completed': lessons_completed,
                'total_score': total_score,
                'rank': 0  # Rank will be assigned after sorting
            })

        # Sort by total_score and lessons_completed
        leaderboard.sort(key=lambda x: (-x['total_score'], -x['lessons_completed']))

        # Assign ranks
        for index, entry in enumerate(leaderboard):
            entry['rank'] = index + 1

        return leaderboard
    

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}"


class LearningMaterial(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    lesson = models.ForeignKey(Lesson, related_name='materials', on_delete=models.CASCADE)
    link = models.URLField(blank=True, null=True)