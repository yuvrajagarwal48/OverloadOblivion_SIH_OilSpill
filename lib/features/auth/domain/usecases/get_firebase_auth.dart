
import 'package:firebase_auth/firebase_auth.dart';
import 'package:fpdart/fpdart.dart';
import 'package:spill_sentinel/core/error/failure.dart';
import 'package:spill_sentinel/core/usecase/usecase.dart';
import 'package:spill_sentinel/features/auth/domain/repository/auth_repository.dart';

class GetFirebaseAuth implements Usecase<FirebaseAuth, NoParams> {
  final AuthRepository repository;

  GetFirebaseAuth(this.repository);

  @override
  Future<Either<Failure,FirebaseAuth>> call(NoParams params) async {
    return await repository.getFirebaseAuth();
  }
}