
import 'package:fpdart/fpdart.dart';
import 'package:spill_sentinel/core/error/failure.dart';
import 'package:spill_sentinel/core/usecase/usecase.dart';
import 'package:spill_sentinel/features/auth/domain/repository/auth_repository.dart';


class VerifyUserEmail implements Usecase<void,NoParams> {
  final AuthRepository authRepository;
  const VerifyUserEmail(this.authRepository);
  @override
  Future<Either<Failure,bool>> call(NoParams params) async{
    return authRepository.verifyEmail();
  }
}
