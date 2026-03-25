import strawberry
from app.presentation.graphql.resolvers.exercise import ExerciseQuery
from app.presentation.graphql.resolvers.routine import RoutineQuery
from app.presentation.graphql.resolvers.mesocycle import MesocycleQuery
from app.presentation.graphql.resolvers.session import SessionQuery
from app.presentation.graphql.resolvers.bodyweight import BodyweightQuery
from app.presentation.graphql.resolvers.calendar import CalendarQuery
from app.presentation.graphql.resolvers.insight import InsightQuery

from app.presentation.graphql.mutations.exercise import ExerciseMutation
from app.presentation.graphql.mutations.routine import RoutineMutation
from app.presentation.graphql.mutations.mesocycle import MesocycleMutation
from app.presentation.graphql.mutations.session import SessionMutation
from app.presentation.graphql.mutations.bodyweight import BodyweightMutation
from app.presentation.graphql.mutations.backup import BackupMutation

from app.presentation.middleware.error_handler import ErrorHandlerExtension

@strawberry.type
class Query(
    ExerciseQuery, 
    RoutineQuery, 
    MesocycleQuery, 
    SessionQuery, 
    BodyweightQuery, 
    CalendarQuery, 
    InsightQuery
):
    pass

@strawberry.type
class Mutation(
    ExerciseMutation, 
    RoutineMutation, 
    MesocycleMutation, 
SessionMutation, 
    BodyweightMutation, 
    BackupMutation
):
    pass

schema = strawberry.Schema(
    query=Query, 
    mutation=Mutation,
    extensions=[ErrorHandlerExtension]
)
