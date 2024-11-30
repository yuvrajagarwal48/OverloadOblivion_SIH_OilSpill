
import 'package:fpdart/fpdart.dart';
import 'package:spill_sentinel/core/entities/user_entity.dart';
import 'package:spill_sentinel/core/error/failure.dart';
import 'package:spill_sentinel/features/auth/domain/repository/auth_repository.dart';


import 'usecase.dart';

class CurrentUser implements Usecase<User,NoParams>{
  final AuthRepository repository;

  CurrentUser(this.repository);

  @override
  Future<Either<Failure,User>> call(NoParams params) async {
    return await repository.getCurrentUser();
  }
}