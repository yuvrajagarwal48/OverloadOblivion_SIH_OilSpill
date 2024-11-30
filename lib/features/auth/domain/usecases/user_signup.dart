

import 'package:fpdart/fpdart.dart';
import 'package:spill_sentinel/core/entities/user_entity.dart';
import 'package:spill_sentinel/core/error/failure.dart';
import 'package:spill_sentinel/core/usecase/usecase.dart';
import 'package:spill_sentinel/features/auth/domain/repository/auth_repository.dart';


class UserSignup implements Usecase<User, UserSignupParams> {
  final AuthRepository authRepository;
  const UserSignup(this.authRepository);
  @override
  Future<Either<Failure, User>> call(UserSignupParams params) async {
    return await authRepository.signInWithEmailAndPassword(
      middleName: params.middleName,
      lastName: params.lastName, firstName: params.firstName, email: params.email, password: params.password);
  }
}

class UserSignupParams {
  final String firstName;
  final String middleName;
  final String lastName;
  final String email;
  final String password;

  UserSignupParams(
      {required this.firstName,required this.middleName,required this.lastName,  required this.email, required this.password});

}
