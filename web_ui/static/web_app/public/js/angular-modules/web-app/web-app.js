/**
 * Angular JavaScript that controls the user interface interactions .
 * @module App module
 * @author Santiago Flores Kanter <sfloresk@cisco.com>
 * @copyright Copyright (c) 2018 Cisco and/or its affiliates.
 * @license Cisco Sample Code License, Version 1.0
 */

/**
 * @license
 * Copyright (c) 2018 Cisco and/or its affiliates.
 *
 * This software is licensed to you under the terms of the Cisco Sample
 * Code License, Version 1.0 (the "License"). You may obtain a copy of the
 * License at
 *
 *                https://developer.cisco.com/docs/licenses
 *
 * All use of the material herein must be in accordance with the terms of
 * the License. All rights not expressly granted by the License are
 * reserved. Unless required by applicable law or agreed to separately in
 * writing, software distributed under the License is distributed on an "AS
 * IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
 * or implied.
 */
 /* Global variables */

var appModule = angular.module('appModule',['ngRoute','ngAnimate'])

/*  Configuration    */

// To avoid conflicts with other template tools such as Jinja2, all between {a a} will be managed by ansible instead of {{ }}
appModule.config(['$interpolateProvider', function($interpolateProvider) {
  $interpolateProvider.startSymbol('{a');
  $interpolateProvider.endSymbol('a}');
}]);


// Application routing
appModule.config(function($routeProvider, $locationProvider){
    // Maps the URLs to the templates located in the server
    $routeProvider
        .when('/', {templateUrl: 'ng/home'})
        .when('/home', {templateUrl: 'ng/home'})
        .when('/apMetrics', {templateUrl: 'ng/apMetrics'})
        .when('/settings', {templateUrl: 'ng/settings'})
    $locationProvider.html5Mode(true);
});




function property(){
    function parseString(input){
        return input.split(".");
    }

    function getValue(element, propertyArray){
        var value = element;

        _.forEach(propertyArray, function(property){
            value = value[property];
        });

        return value;
    }

    return function (array, propertyString, target){
        var properties = parseString(propertyString);

        return _.filter(array, function(item){
            return getValue(item, properties).toUpperCase().startsWith(target.toUpperCase());
        });
    }
}

appModule.filter('property', property);

/*  Controllers    */



// App controller is in charge of managing all services for the application
appModule.controller('AppController', function($scope, $location, $http, $window, $rootScope){

    $scope.error = ""
    $scope.success = ""
    $scope.loading = false;

    $scope.fiveGClients = 0
    $scope.twoPointFourGClients = 0
    $scope.averageChannelUtilization = 0;
    $scope.poorCoverageClientsPercentage = 0;
    $scope.collection = []
    $scope.collectionStatus = "dead"
    $scope.settings = {}
    $scope.newSettings = {}
    $scope.search = {}
    $scope.search.apName = ""
    $scope.newSettings = {}


    $scope.go = function ( path ) {
        $location.path( path );
    };


    $scope.clearError = function(){
        $scope.error = "";
    };
    $scope.clearSuccess = function(){
        $scope.success = "";
    };

    $scope.getCollection= function(){
        $scope.loading = true;
        $http
            .get('api/collection')
            .then(function (response, status, headers, config){
                $scope.collection = response.data
                var channelUtilizationSum = 0;
                var poorCoverageClientsSum = 0;
                $scope.fiveGClients = 0;
                $scope.twoPointFourGClients = 0;
                channelUtilizationSum = 0;
                poorCoverageClientsSum = 0;

                for (var row in $scope.collection) {
                    $scope.fiveGClients+= $scope.collection[row].fields.fiveGClients;
                    $scope.twoPointFourGClients += $scope.collection[row].fields.twoGClients;
                    $scope.twoPointFourGClients += $scope.collection[row].fields.twoGClients;
                    channelUtilizationSum += $scope.collection[row].fields.channelUtilization;
                    poorCoverageClientsSum += $scope.collection[row].fields.poorCoverageClients;

                }
                $scope.averageChannelUtilization = parseInt(channelUtilizationSum / $scope.collection.length)
                $scope.poorCoverageClientsPercentage = parseInt( poorCoverageClientsSum/ ($scope.twoPointFourGClients+$scope.fiveGClients))


            })
            .catch(function(response, status, headers, config){
                $scope.error = response.data.message
            })
            .finally(function(){
                $scope.loading = false;
            })
    };

    $scope.startCollection= function(){

        $http
            .post('api/collection')
            .then(function (response, status, headers, config){
                  $scope.success = "Collection Started!";
            })
            .catch(function(response, status, headers, config){
                $scope.error = response.data.message
            })
            .finally(function(){
            })
    };
    $scope.getCollectionStatus= function(){

        $http
            .get('api/collection/status')
            .then(function (response, status, headers, config){
                if($scope.collectionStatus != "dead" && response.data.status == "dead"){
                    // Refresh collection
                    $scope.getCollection()
                }
                $scope.collectionStatus = response.data.status

            })
            .catch(function(response, status, headers, config){
                $scope.error = response.data.message
            })
            .finally(function(){
            })
    };

    $scope.getSettings= function(){
        $http
            .get('api/settings')
            .then(function (response, status, headers, config){

                $scope.settings = response.data

            })
            .catch(function(response, status, headers, config){
                $scope.error = response.data.message
            })
            .finally(function(){
            })
    };

    $scope.setSettings= function(){
        $http
            .post('api/settings',$scope.newSettings)
            .then(function (response, status, headers, config){

                $scope.success = "Settings Updated"
                $scope.getSettings();

            })
            .catch(function(response, status, headers, config){
                $scope.error = response.data.message
            })
            .finally(function(){
            })
    };


    $scope.getSettings();
    $scope.getCollection();
    setInterval($scope.getCollectionStatus,2000)

});
