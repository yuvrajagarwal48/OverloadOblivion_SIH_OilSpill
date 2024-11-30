
import 'package:firebase_auth/firebase_auth.dart' as auth;

import 'package:fpdart/src/either.dart';
import 'package:spill_sentinel/core/entities/user_entity.dart';
import 'package:spill_sentinel/core/error/failure.dart';
import 'package:spill_sentinel/core/error/server_exception.dart';
import 'package:spill_sentinel/core/network/check_internet_connection.dart';
import 'package:spill_sentinel/features/auth/data/datasources/auth_remote_datasources.dart';
import 'package:spill_sentinel/features/auth/domain/repository/auth_repository.dart';


class AuthRepositoryImpl implements AuthRepository {
  final AuthRemoteDataSources authRemoteDatasources;
  final CheckInternetConnection checkInternetConnection;
  const AuthRepositoryImpl(
      this.authRemoteDatasources, this.checkInternetConnection);
  @override
  Future<Either<Failure, User>> loginWithEmailAndPassword(
      {required String email, required String password}) {
    return _getUser(() async => await authRemoteDatasources
        .loginWithEmailAndPassword(email: email, password: password));
  }

  @override
  Future<Either<Failure, User>> signInWithEmailAndPassword(
      {required String firstName,
      required String lastName,
      required String middleName,
      required String email,
      required String password}) {
    return _getUser(() async =>
        await authRemoteDatasources.signUpWithEmailAndPassword(
            firstName: firstName,
            middleName: middleName,
            lastName: lastName,
            email: email,
            password: password));
  }

  Future<Either<Failure, User>> _getUser(Future<User> Function() fn) async {
    try {
      bool isConnected = await checkInternetConnection.isConnected;
      if (!isConnected) {
        return Left(Failure('No internet connection'));
      }
      final user = await fn();
      return Right(user);
    } on ServerException catch (e) {
      return Left(Failure(e.message));
    }
  }

  @override
  Future<Either<Failure, User>> getCurrentUser() async {
    try {
      if (!await checkInternetConnection.isConnected) {
        return Left(Failure('No internet connection'));
      }
      final user = await authRemoteDatasources.getCurrentUser();
      if (user == null) {
        return Left(Failure('User is not logged in'));
      }
      return Right(user);
    } on ServerException catch (e) {
      return Left(Failure(e.toString()));
    }
  }

  @override
  Future<Either<Failure, User>> signInWithGoogle() {
    return _getUser(() async => await authRemoteDatasources.signInWithGoogle());
  }

  @override
  Future<Either<Failure, bool>> verifyEmail() async {
    try {
      if (!await checkInternetConnection.isConnected) {
        return Left(Failure('No internet connection'));
      }

      await authRemoteDatasources.verifyEmail();
      return const Right(true);
    } catch (e) {
      return Left(Failure(e.toString()));
    }
  }

  @override
  Future<Either<Failure, auth.FirebaseAuth>> getFirebaseAuth() async {
    try {
      if (!await checkInternetConnection.isConnected) {
        return Left(Failure('No internet connection'));
      }
      final firebaseAuth = await authRemoteDatasources.getFirebaseAuth();
      return Right(firebaseAuth);
    } catch (e) {
      return Left(Failure(e.toString()));
    }
  }

  @override
  Future<Either<Failure, bool>> isUserEmailVerified() async {
    try {
      if (!await checkInternetConnection.isConnected) {
        return Left(Failure('No internet connection'));
      }
      final isVerified = await authRemoteDatasources.isUserEmailVerified();
      return Right(isVerified);
    } catch (e) {
      return Left(Failure(e.toString()));
    }
  }

  @override
  Future<Either<Failure, void>> updateEmailVerification() async{
    try {
      if (!await checkInternetConnection.isConnected) {
        return Left(Failure('No internet connection'));
      }
      return Right(authRemoteDatasources.updateEmailVerification());
    } catch (e) {
      return Left(Failure(e.toString()));
    }
  }
}
