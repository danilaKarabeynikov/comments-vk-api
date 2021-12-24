
-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema vkdb
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema vkdb
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `vkdb` DEFAULT CHARACTER SET utf8 ;
USE `vkdb` ;

-- -----------------------------------------------------
-- Table `vkdb`.`posts`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `vkdb`.`posts` (
  `idposts` INT NOT NULL,
  `ownerid` INT NOT NULL,
  `date` INT NOT NULL,
  `text` LONGTEXT NULL,
  `countOfComments` INT UNSIGNED NULL,
  `countOfLikes` INT UNSIGNED NULL,
  `countOfReposts` INT UNSIGNED NULL,
  `countOfViews` INT UNSIGNED NULL,
  PRIMARY KEY (`idposts`))
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `vkdb`.`comments` (
  `idcomments` INT NOT NULL,
  `id_idposts` INT NOT NULL,
  `fromID` INT NOT NULL,
  `date` INT NOT NULL,
  `text` LONGTEXT NULL,
  `idrecomments` INT NULL,
  PRIMARY KEY (`idcomments`),
  INDEX `fk_comments_posts_idx` (`id_idposts` ASC) VISIBLE,
  INDEX `fk_comments_comments1_idx` (`idrecomments` ASC) VISIBLE,
  CONSTRAINT `fk_comments_posts`
    FOREIGN KEY (`id_idposts`)
    REFERENCES `vkdb`.`posts` (`idposts`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_comments_comments1`
    FOREIGN KEY (`idrecomments`)
    REFERENCES `vkdb`.`comments` (`idcomments`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
